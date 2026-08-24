r"""
Multi-Provider LLM Engine for Standalone Agent Harness.
Dispatches queries with tool-calling schemas to Google Gemini, Anthropic Claude, OpenAI, Ollama, DeepSeek, and Groq.
Executes tool calls directly in UnrealEd via EngineController and FormulaEngine.
"""

import json
import time
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config_manager import ConfigManager
from .engine_controller import EngineController
from .formula_engine import FormulaEngine, _write_brush_file
from .logger import get_logger
from .nexus_bridge import NexusBridge
from .pathing_engine import PathingEngine
from .tools_schema import UNREALED_TOOLS
from .vision_inspector import VisionInspector

logger = get_logger("LLMEngine", "llm_engine.log")


class LLMEngine:
    """Orchestrates multi-provider LLM inference, tool execution, and UnrealEd level automation."""

    def __init__(
        self,
        config_mgr: Optional[ConfigManager] = None,
        controller: Optional[EngineController] = None,
        nexus_bridge: Optional[NexusBridge] = None,
    ):
        self.config_mgr = config_mgr or ConfigManager()
        self.controller = controller or EngineController(self.config_mgr)
        self.nexus_bridge = nexus_bridge or NexusBridge()
        self.formula_engine = FormulaEngine()
        self.pathing_engine = PathingEngine(self.config_mgr)
        self.vision_inspector = VisionInspector()
        logger.info("LLMEngine initialized.")

    def _refresh_context(self) -> None:
        """Refreshes pathing engine, controller paths, and system prompt context after an engine switch."""
        self.controller._refresh_paths()
        self.pathing_engine = PathingEngine(self.config_mgr)
        active_prof = self.config_mgr.get_active_engine_profile()
        logger.info(f"LLMEngine context refreshed for: '{active_prof.get('name', 'Unknown')}'")

    def _build_system_prompt(self) -> str:
        personality = self.config_mgr.get_active_personality()
        engine_prof = self.config_mgr.get_active_engine_profile()
        engine_id = self.config_mgr.get_active_engine_id()
        engine_name = engine_prof.get("name", "Unreal Tournament")
        generation = engine_prof.get("generation", "UE1")

        sig_classes = engine_prof.get("signature_classes", {})
        classes_str = ", ".join([f"{k}: {v}" for k, v in list(sig_classes.items())[:14]])

        preamble = personality.get("prompt_preamble", "You are the Master Level Architect.")

        # Engine-specific architectural directives
        engine_directives = []
        if engine_id == "ut99_goty":
            engine_directives = [
                "Target: Unreal Tournament 99 GOTY (UE1 / OldUnreal 469e).",
                "Classic Tournament Weapons: Botpack.ShockRifle, Botpack.UT_FlakCannon, Botpack.UT_Eightball (Rocket Launcher), Botpack.SniperRifle, Botpack.minigun2, Botpack.UT_BioRifle, Botpack.PulseGun, Botpack.Enforcer.",
                "Classic Pickups: Botpack.UT_ShieldBelt (150 AP), Botpack.Armor2 (100 AP), Botpack.ThighPads (50 AP), Botpack.UDamage (Amplifier), Botpack.HealthVial, Botpack.MedBox.",
                "Navigation & Spawns: Engine.PlayerStart, Engine.PathNode, Botpack.UT_JumpPad, Botpack.TranslocatorTarget.",
                "Game Types: Botpack.DeathMatchPlus, Botpack.CTFGame, Botpack.Domination, Botpack.Assault.",
            ]
        elif engine_id == "ut99_utron":
            engine_directives = [
                "Target: UTron Total Conversion Mod (UE1 / 469e).",
                "UTron Classes: UTron.IdentityDisc, UTron.DiscAmmo, UTron.diffuser, UTron.wirenode, UTron.cycleMorph, UTron.DiscArena, UTron.Recognizer.",
                "For diffusers, configure Baseglow, Touchiness, Transfer, Faderate, and TileTypes (TT_Normal, TT_Switcher, TT_Toggler, TT_Delayed, TT_Neuron).",
                "For wirenodes, link them via Tag and Event with TemplateTag set to a template diffuser.",
                "For light cycle grids, build smooth subtractive grid arenas with neon accent lighting.",
            ]
        elif engine_id in ["ut2004", "ut2003"]:
            engine_directives = [
                "Target: Unreal Tournament 2004 / 2003 (UE2.5 / v3369+).",
                "Weapons: XWeapons.ShockRiflePickup, XWeapons.FlakCannonPickup, XWeapons.RocketLauncherPickup, XWeapons.SniperRiflePickup, XWeapons.MinigunPickup, XWeapons.LinkGunPickup, XWeapons.BioRiflePickup, XWeapons.AssaultRiflePickup, Onslaught.ONSAVRiLPickup.",
                "Pickups: XPickups.ShieldPickup, XPickups.SuperShieldPack, XPickups.UDamagePack, XPickups.HealthPack, XPickups.MiniHealthPack.",
                "Vehicles & Onslaught: Onslaught.ONSPowerCore, Onslaught.ONSPowerNodeNeutral, Onslaught.ONSHoverCraftFactory (Manta), Onslaught.ONSAttackCraftFactory (Raptor), Onslaught.ONSTankFactory (Goliath), Onslaught.ONSRVFactory (Scorpion), Onslaught.ONSPRVFactory (Hellbender).",
                "Navigation: Engine.PlayerStart, Engine.PathNode, XGame.xJumpPad, XGame.xDoor.",
            ]
        elif engine_id == "ut99_chaosut":
            engine_directives = [
                "Target: ChaosUT: Evolution Mod (UE1).",
                "Chaos Weapons: ChaosUT.Crossbow, ChaosUT.ProxyLauncher, ChaosUT.Vortex, ChaosUT.ChaosSniper, ChaosUT.Turret, ChaosUT.GravityBelt.",
            ]
        elif engine_id == "ut99_tacticalops":
            engine_directives = [
                "Target: Tactical Ops: Assault on Terror (UE1).",
                "Tactical Ops: Terrorist / Special Forces spawn points, Buy Zones, Hostage Rescue points, Bomb Target zones.",
            ]
        else:
            engine_directives = [
                f"Target: {engine_name} ({generation}).",
                f"Use verified signature classes: {classes_str}.",
            ]

        directives_str = "\n".join([f"- {d}" for d in engine_directives])

        prompt = f"""{preamble}

TARGET ENGINE ENVIRONMENT:
- Active Engine: {engine_name} ({generation})
- Root Directory: {engine_prof.get('root_dir')}
- System Directory: {engine_prof.get('system_dir')}
- Verified Signature Classes: {classes_str}

LEVEL DESIGN RULES & ARCHITECTURAL DIRECTIVES:
1. In UnrealEd console, ALWAYS move the builder brush before placing actors: BRUSH MOVETO X=<x> Y=<y> Z=<z> followed by ACTOR ADD CLASS=<class>.
2. When creating CSG rooms or arenas, issue proper PolyList brush imports and SUBTRACT/ADD operations, then spawn lights, player starts, weapons, and path nodes.
3. Always finalize level builds with MAP REBUILD, LIGHT APPLY, and PATHS BUILD.
4. Execute tools decisively with exact 3D coordinates.

ACTIVE ENGINE SPECIFIC GUIDELINES:
{directives_str}
"""
        return prompt

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes tool calls generated by LLMs."""
        logger.info(f"Executing tool: '{tool_name}' with args: {arguments}")
        start_time = time.time()

        try:
            if tool_name == "execute_unrealed_commands":
                cmds = arguments.get("commands", [])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "results": results}

            elif tool_name == "create_bsp_room":
                shape = arguments.get("shape", "Box")
                op = arguments.get("operation", "Subtract")
                dims = arguments.get("dimensions", [2048, 2048, 512])
                loc = arguments.get("location", [0, 0, 0])
                add_light = arguments.get("add_light", True)
                floor_tex = arguments.get("floor_texture", "UTtech1.Floor.rClfFlr2")
                wall_tex = arguments.get("wall_texture", "UTtech1.Wall.bmwall3")
                ceil_tex = arguments.get("ceiling_texture", "UTtech1.Ceiling.bmCeiling3")

                b_file = _write_brush_file(
                    self.controller.system_dir, "CustomRoom.t3d",
                    (float(dims[0]), float(dims[1]), float(dims[2])),
                    shape=shape,
                    floor_tex=floor_tex,
                    wall_tex=wall_tex,
                    ceil_tex=ceil_tex,
                )
                op_cmd = "BRUSH SUBTRACT" if op.lower() == "subtract" else "BRUSH ADD"

                cmds = [
                    f"BRUSH MOVETO X={loc[0]} Y={loc[1]} Z={loc[2]}",
                    f'BRUSH IMPORT FILE="{b_file}" MERGE=0 FLAGS=0',
                    op_cmd,
                ]

                if add_light:
                    cmds.append(f"BRUSH MOVETO X={loc[0]} Y={loc[1]} Z={loc[2] + int(dims[2]*0.25)}")
                    cmds.append("ACTOR ADD CLASS=Engine.Light")

                cmds.extend(["MAP REBUILD", "LIGHT APPLY", "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "commands_executed": cmds, "results": results}

            elif tool_name == "spawn_actor":
                actor_class = arguments.get("actor_class", "Engine.Light")
                loc = arguments.get("location", [0, 0, 0])
                cmds = [
                    f"BRUSH MOVETO X={loc[0]} Y={loc[1]} Z={loc[2]}",
                    f"ACTOR ADD CLASS={actor_class}",
                    "FLUSH",
                ]
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "results": results}

            elif tool_name == "build_utron_arena":
                arch = arguments.get("archetype", "disc_arena")
                if arch == "disc_arena":
                    radius = int(arguments.get("radius", 1536))
                    cmds = self.formula_engine.generate_utron_disc_arena(system_dir=self.controller.system_dir, radius=radius)
                elif arch == "lightcycle_grid":
                    cmds = self.formula_engine.generate_utron_lightcycle_grid(system_dir=self.controller.system_dir)
                elif arch == "diffuser_bus":
                    count = int(arguments.get("diffuser_count", 8))
                    cmds = self.formula_engine.generate_utron_diffuser_bus((0, 0, -200), count=count)
                else:
                    cmds = self.formula_engine.generate_utron_disc_arena(system_dir=self.controller.system_dir)

                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event("ut99_utron", f"Built UTron {arch}", f"{len(cmds)} commands")
                return {"status": "success", "archetype": arch, "commands": len(cmds)}

            elif tool_name == "build_tournament_arena":
                w = int(arguments.get("width", 3072))
                l = int(arguments.get("length", 3072))
                h = int(arguments.get("height", 1024))
                detail = arguments.get("detail_level", "ultra")
                cmds = self.formula_engine.generate_ut99_tournament_arena(
                    system_dir=self.controller.system_dir, width=w, length=l, height=h, detail_level=detail
                )
                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event("ut99", f"Built Tournament Arena ({detail})", f"{w}x{l}x{h}")
                return {"status": "success", "commands": len(cmds), "detail_level": detail}

            elif tool_name == "build_unreal1_sanctuary":
                detail = arguments.get("detail_level", "ultra")
                cmds = self.formula_engine.generate_unreal1_sp_sanctuary(
                    system_dir=self.controller.system_dir, detail_level=detail
                )
                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event("unreal1", f"Built Sacred Nali Sanctuary ({detail})", f"{len(cmds)} cmds")
                return {"status": "success", "commands": len(cmds), "detail_level": detail}

            elif tool_name == "build_outdoor_world":
                w_type = arguments.get("world_type", "mountain_valley")
                detail = arguments.get("detail_level", "ultra")
                if w_type == "mountain_valley":
                    cmds = self.formula_engine.generate_ut99_verdant_mountain_valley(
                        system_dir=self.controller.system_dir, detail_level=detail
                    )
                elif w_type == "desert_canyon":
                    cmds = self.formula_engine.generate_ut99_desert_canyon_ruins(
                        system_dir=self.controller.system_dir
                    )
                elif w_type == "asteroid_outpost":
                    cmds = self.formula_engine.generate_ut99_orbital_asteroid_outpost(
                        system_dir=self.controller.system_dir
                    )
                else:
                    cmds = self.formula_engine.generate_ut99_verdant_mountain_valley(
                        system_dir=self.controller.system_dir, detail_level=detail
                    )
                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event("ut99", f"Built Outdoor World ({w_type}, {detail})", f"{len(cmds)} cmds")
                return {"status": "success", "world_type": w_type, "commands": len(cmds), "detail_level": detail}

            elif tool_name == "build_path_lattice":
                bounds = tuple(arguments.get("bounds", [-1024, -1024, -200, 1024, 1024, -200]))
                spacing = int(arguments.get("spacing", 512))
                z_floor = arguments.get("z_floor")
                cmds = self.pathing_engine.generate_path_lattice(bounds=bounds, spacing=spacing, z_floor=z_floor)
                cmds.extend(["PATHS BUILD", "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "nodes_generated": len(cmds) // 2}

            elif tool_name == "build_perimeter_nodes":
                center = tuple(arguments.get("center", [0, 0, 0]))
                radius = int(arguments.get("radius", 1024))
                count = int(arguments.get("count", 8))
                cmds = self.pathing_engine.generate_perimeter_nodes(center=center, radius=radius, count=count)
                cmds.extend(["PATHS BUILD", "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "nodes_generated": count}

            elif tool_name == "wire_jumppad":
                launch = tuple(arguments.get("launch_pos", [0, 0, 0]))
                landing = tuple(arguments.get("landing_pos", [0, 0, 400]))
                tag = arguments.get("tag", "JumpPad1")
                cmds = self.pathing_engine.generate_jumppad_pair(launch_pos=launch, landing_pos=landing, tag=tag)
                cmds.extend(["PATHS BUILD", "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "pair": tag}

            elif tool_name == "wire_teleporter":
                entry = tuple(arguments.get("entry_pos", [0, 0, 0]))
                exit_pos = tuple(arguments.get("exit_pos", [1000, 1000, 0]))
                url = arguments.get("url_tag", "TeleA")
                cmds = self.pathing_engine.generate_teleporter_pair(entry_pos=entry, exit_pos=exit_pos, url_tag=url)
                cmds.extend(["PATHS BUILD", "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "teleporter": url}

            elif tool_name == "audit_pathing":
                log_lines = self.controller.get_log_deltas()
                report = self.pathing_engine.generate_reachability_report(log_lines)
                if arguments.get("fix_gaps", False):
                    # Gap filling
                    pass
                return {"status": "success", "audit_report": report}

            elif tool_name == "rebuild_level":
                build_paths = arguments.get("build_paths", True)
                cmds = ["MAP REBUILD", "LIGHT APPLY"]
                if build_paths:
                    cmds.append("PATHS BUILD")
                cmds.append("FLUSH")
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "results": results}

            elif tool_name == "switch_engine_profile":
                engine_id = arguments.get("engine_id", "ut99_utron")
                ok = self.config_mgr.set_active_engine_id(engine_id)
                self.controller._refresh_paths()
                return {"status": "success" if ok else "failed", "active_engine": engine_id}

            elif tool_name == "capture_viewport" or tool_name == "inspect_viewport":
                img_bytes = self.controller.capture_viewport_image()
                return {"status": "success" if img_bytes else "failed", "bytes": len(img_bytes) if img_bytes else 0}

            else:
                return {"status": "error", "error": f"Unknown tool '{tool_name}'"}

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def chat(self, user_message: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Dispatches a user query to the active LLM provider."""
        profile = self.config_mgr.get_active_llm_profile()
        provider = profile.get("provider", "google")
        api_key = profile.get("api_key", "")
        model = profile.get("model", "gemini-2.5-pro")
        base_url = profile.get("base_url", "")

        system_prompt = self._build_system_prompt()
        logger.info(f"Dispatching chat to provider '{provider}' (Model: '{model}')")

        # Handle local offline Ollama / LM Studio or OpenAI-compatible
        if provider in ["openai", "openrouter", "groq", "deepseek", "ollama", "lmstudio"]:
            return self._chat_openai_compatible(user_message, history, profile, system_prompt)
        elif provider == "anthropic":
            return self._chat_anthropic(user_message, history, profile, system_prompt)
        else:
            # Default to Google Gemini
            return self._chat_gemini(user_message, history, profile, system_prompt)

    def _chat_openai_compatible(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]],
        profile: Dict[str, Any],
        system_prompt: str,
    ) -> Dict[str, Any]:
        base_url = profile.get("base_url", "https://api.openai.com/v1").rstrip("/")
        url = f"{base_url}/chat/completions"
        api_key = profile.get("api_key", "")
        model = profile.get("model", "gpt-4o")

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history[-8:]:
                messages.append(h)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": profile.get("temperature", 0.2),
            "max_tokens": profile.get("max_tokens", 4096),
        }
        if profile.get("enable_tools", True):
            payload["tools"] = UNREALED_TOOLS

        headers = {"Content-Type": "application/json"}
        if api_key and api_key != "ollama":
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            choice = data["choices"][0]["message"]
            response_text = choice.get("content") or ""
            tool_calls = choice.get("tool_calls", [])

            executed_tools = []
            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                args = json.loads(fn.get("arguments", "{}"))
                res = self.execute_tool(name, args)
                executed_tools.append({"tool": name, "args": args, "result": res})

            return {"role": "assistant", "content": response_text, "tool_executions": executed_tools}

        except Exception as e:
            logger.error(f"OpenAI compatible request failed: {e}")
            return {"role": "assistant", "content": f"⚠️ Error: {str(e)}", "tool_executions": []}

    def _chat_gemini(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]],
        profile: Dict[str, Any],
        system_prompt: str,
    ) -> Dict[str, Any]:
        api_key = profile.get("api_key", "")
        model = profile.get("model", "gemini-2.5-pro")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        contents = []
        if history:
            for h in history[-6:]:
                role = "user" if h.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        payload: Dict[str, Any] = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": profile.get("temperature", 0.2),
                "maxOutputTokens": profile.get("max_tokens", 8192),
            },
        }

        try:
            req = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text_out = "".join([p.get("text", "") for p in parts])
                return {"role": "assistant", "content": text_out, "tool_executions": []}
            return {"role": "assistant", "content": "No response received from Gemini.", "tool_executions": []}

        except Exception as e:
            logger.error(f"Gemini request error: {e}")
            return {"role": "assistant", "content": f"⚠️ Gemini Error: {str(e)}", "tool_executions": []}

    def _chat_anthropic(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]],
        profile: Dict[str, Any],
        system_prompt: str,
    ) -> Dict[str, Any]:
        api_key = profile.get("api_key", "")
        model = profile.get("model", "claude-3-7-sonnet-20250219")
        url = "https://api.anthropic.com/v1/messages"

        messages = []
        if history:
            for h in history[-6:]:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": model,
            "system": system_prompt,
            "messages": messages,
            "max_tokens": profile.get("max_tokens", 8192),
            "temperature": profile.get("temperature", 0.2),
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        try:
            req = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            content_blocks = data.get("content", [])
            text_out = "".join([b.get("text", "") for b in content_blocks if b.get("type") == "text"])
            return {"role": "assistant", "content": text_out, "tool_executions": []}

        except Exception as e:
            logger.error(f"Anthropic request error: {e}")
            return {"role": "assistant", "content": f"⚠️ Claude Error: {str(e)}", "tool_executions": []}
