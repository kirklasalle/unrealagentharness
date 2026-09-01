r"""
Multi-Provider LLM Engine for Standalone Agent Harness.
Dispatches queries with full native tool-calling schemas to Google Gemini, Anthropic Claude, OpenAI, Ollama, DeepSeek, and Groq.
Executes tool calls directly in UnrealEd via EngineController and FormulaEngine, with persistent MemoryEngine wisdom integration.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config_manager import ConfigManager
from .engine_controller import EngineController
from .formula_engine import FormulaEngine, _write_brush_file
from .logger import get_logger
from .memory_engine import MemoryEngine
from .nexus_bridge import NexusBridge
from .pathing_engine import PathingEngine
from .tools_schema import UNREALED_TOOLS
from .vision_inspector import VisionInspector

logger = get_logger("LLMEngine", "llm_engine.log")


def _tools_to_gemini_schema(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts OpenAI-style tool definitions to Google Gemini functionDeclarations format."""
    declarations = []
    for t in tools:
        fn = t.get("function", {})
        params = fn.get("parameters", {"type": "object", "properties": {}})
        declarations.append({
            "name": fn.get("name", ""),
            "description": fn.get("description", ""),
            "parameters": params,
        })
    return [{"functionDeclarations": declarations}]


def _tools_to_anthropic_schema(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts OpenAI-style tool definitions to Anthropic Claude input_schema format."""
    claude_tools = []
    for t in tools:
        fn = t.get("function", {})
        claude_tools.append({
            "name": fn.get("name", ""),
            "description": fn.get("description", ""),
            "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
        })
    return claude_tools


class LLMEngine:
    """Orchestrates multi-provider LLM inference, native tool execution, and UnrealEd level automation."""

    def __init__(
        self,
        config_mgr: Optional[ConfigManager] = None,
        controller: Optional[EngineController] = None,
        nexus_bridge: Optional[NexusBridge] = None,
        memory_engine: Optional[MemoryEngine] = None,
    ):
        self.config_mgr = config_mgr or ConfigManager()
        self.controller = controller or EngineController(self.config_mgr)
        self.nexus_bridge = nexus_bridge or NexusBridge()
        self.formula_engine = FormulaEngine()
        self.pathing_engine = PathingEngine(self.config_mgr)
        self.vision_inspector = VisionInspector()
        self.memory_engine = memory_engine or MemoryEngine()

        # Seed documentation knowledge base into memory index
        try:
            self.memory_engine.index_documentation_directory()
        except Exception as e:
            logger.debug(f"Knowledge base indexing note: {e}")

        logger.info("LLMEngine initialized with native tool calling and MemoryEngine integration.")

    def _refresh_context(self) -> None:
        """Refreshes pathing engine, controller paths, and system prompt context after an engine switch."""
        self.controller._refresh_paths()
        self.pathing_engine = PathingEngine(self.config_mgr)
        active_prof = self.config_mgr.get_active_engine_profile()
        logger.info(f"LLMEngine context refreshed for: '{active_prof.get('name', 'Unknown')}'")

    def _build_system_prompt(self, user_query: str = "") -> str:
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

        # Dynamic Memory Context Augmentation (RAG)
        augmented_memory = ""
        if user_query:
            try:
                augmented_memory = self.memory_engine.build_augmented_context(user_query, engine_id)
            except Exception as e:
                logger.debug(f"Memory augmentation note: {e}")

        prompt = f"""{preamble}

TARGET ENGINE ENVIRONMENT:
- Active Engine: {engine_name} ({generation})
- Root Directory: {engine_prof.get('root_dir')}
- System Directory: {engine_prof.get('system_dir')}
- Verified Signature Classes: {classes_str}

LEVEL DESIGN RULES & ARCHITECTURAL DIRECTIVES:
1. In UnrealEd console, ALWAYS move the builder brush before placing actors: BRUSH MOVETO X=<x> Y=<y> Z=<z> followed by ACTOR ADD CLASS=<class>.
2. When creating CSG rooms or arenas, issue proper PolyList brush imports and SUBTRACT/ADD operations, then spawn lights, player starts, weapons, and path nodes.
3. Always finalize level builds with MAP REBUILD, LIGHT APPLY, and PATHS BUILD (or PATHS DEFINE in UT2004).
4. Execute tools decisively with exact 3D coordinates.

ACTIVE ENGINE SPECIFIC GUIDELINES:
{directives_str}
"""
        if augmented_memory:
            prompt += f"\n\n{augmented_memory}"

        return prompt

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes tool calls generated by LLMs."""
        logger.info(f"Executing tool: '{tool_name}' with args: {arguments}")
        active_engine = self.config_mgr.get_active_engine_id()

        try:
            if tool_name == "analyze_reference_image":
                image_path = arguments.get("image_path", "")
                graph = self.vision_inspector.analyze_reference(image_path)
                source = graph.get("source", {})
                self.memory_engine.record_reference_analysis(
                    scene_id=Path(image_path).stem,
                    source_path=image_path,
                    scene_graph_path=graph.get("scene_graph_path", ""),
                    source_sha256=source.get("sha256", ""),
                    landmark_count=len(graph.get("landmarks", [])),
                )
                return {"status": "success", "scene_graph": graph}

            if tool_name == "build_reference_valley_blockout":
                scene_graph_path = arguments.get("scene_graph_path", "")
                graph = json.loads(Path(scene_graph_path).read_text(encoding="utf-8"))
                cmds = self.formula_engine.generate_ut99_verdant_mountain_valley(
                    system_dir=self.controller.system_dir,
                    detail_level="standard",
                    scene_graph=graph,
                )
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "stage": "macro_blockout", "commands": len(cmds), "results": results}

            if tool_name == "validate_generated_map":
                actor_file = arguments.get("actor_file", "")
                report = self.controller.validate_generated_map(Path(actor_file) if actor_file else None)
                return {"status": "success" if report.get("ok") else "failed", "validation": report}

            if tool_name == "inspect_viewport_quality":
                report = self.controller.capture_viewport_quality()
                return {"status": "success" if report.get("ok") else "failed", "quality": report}

            if tool_name == "configure_unrealed_viewports":
                cfg_res = self.controller.configure_standard_viewports()
                return {"status": "success", "config": cfg_res}

            if tool_name == "capture_standard_quad_view":
                hwnd_main, _, _ = self.controller.find_unrealed_window()
                if not hwnd_main:
                    return {"status": "failed", "error": "UnrealEd window not found"}
                ctx = self.vision_inspector.capture_standard_quad_view(hwnd_main)
                return {"status": "success", "vision_context": ctx}

            if tool_name == "inspect_viewport":
                vp = arguments.get("viewport", "perspective")
                add_grid = arguments.get("add_grid", False)
                hwnd_main, _, _ = self.controller.find_unrealed_window()
                if not hwnd_main:
                    return {"status": "failed", "error": "UnrealEd window not found"}
                if vp == "all":
                    ctx = self.vision_inspector.capture_standard_quad_view(hwnd_main)
                    return {"status": "success", "vision_context": ctx}
                img = self.vision_inspector.capture_viewport(hwnd_main, viewport=vp)
                if img is None:
                    return {"status": "failed", "error": f"Failed to capture viewport '{vp}'"}
                if add_grid:
                    img = self.vision_inspector.annotate_with_grid(img)
                b64 = self.vision_inspector.image_to_base64(img)
                return {
                    "status": "success",
                    "viewport": vp,
                    "width": img.size[0],
                    "height": img.size[1],
                    "base64_png": b64,
                }

            if tool_name == "execute_unrealed_commands":
                cmds = arguments.get("commands", [])
                results = self.controller.execute_batch(cmds)
                self.memory_engine.record_build_event(active_engine, "Custom Batch Commands", len(cmds))
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
                self.memory_engine.record_build_event(active_engine, f"CSG Room ({shape})", len(cmds))
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
                self.memory_engine.record_build_event("ut99_utron", f"UTron {arch}", len(cmds))
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
                self.memory_engine.record_build_event("ut99_goty", f"Tournament Arena ({detail})", len(cmds))
                return {"status": "success", "commands": len(cmds), "detail_level": detail}

            elif tool_name == "build_unreal1_sanctuary":
                detail = arguments.get("detail_level", "ultra")
                cmds = self.formula_engine.generate_unreal1_sp_sanctuary(
                    system_dir=self.controller.system_dir, detail_level=detail
                )
                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event("unreal1", f"Built Sacred Nali Sanctuary ({detail})", f"{len(cmds)} cmds")
                self.memory_engine.record_build_event("unreal1", f"Sacred Nali Sanctuary ({detail})", len(cmds))
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
                self.memory_engine.record_build_event("ut99_goty", f"Outdoor World ({w_type}, {detail})", len(cmds))
                return {"status": "success", "world_type": w_type, "commands": len(cmds), "detail_level": detail}

            elif tool_name == "build_path_lattice":
                bounds = tuple(arguments.get("bounds", [-1024, -1024, -200, 1024, 1024, -200]))
                spacing = int(arguments.get("spacing", 512))
                z_floor = arguments.get("z_floor")
                cmds = self.pathing_engine.generate_path_lattice(bounds=bounds, spacing=spacing, z_floor=z_floor)
                path_build_cmd = "PATHS DEFINE" if active_engine in ["ut2004", "ut2003"] else "PATHS BUILD"
                cmds.extend([path_build_cmd, "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "nodes_generated": len(cmds) // 2}

            elif tool_name == "build_perimeter_nodes":
                center = tuple(arguments.get("center", [0, 0, 0]))
                radius = int(arguments.get("radius", 1024))
                count = int(arguments.get("count", 8))
                cmds = self.pathing_engine.generate_perimeter_nodes(center=center, radius=radius, count=count)
                path_build_cmd = "PATHS DEFINE" if active_engine in ["ut2004", "ut2003"] else "PATHS BUILD"
                cmds.extend([path_build_cmd, "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "nodes_generated": count}

            elif tool_name == "wire_jumppad":
                launch = tuple(arguments.get("launch_pos", [0, 0, 0]))
                landing = tuple(arguments.get("landing_pos", [0, 0, 400]))
                tag = arguments.get("tag", "JumpPad1")
                cmds = self.pathing_engine.generate_jumppad_pair(launch_pos=launch, landing_pos=landing, tag=tag)
                path_build_cmd = "PATHS DEFINE" if active_engine in ["ut2004", "ut2003"] else "PATHS BUILD"
                cmds.extend([path_build_cmd, "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "pair": tag}

            elif tool_name == "wire_teleporter":
                entry = tuple(arguments.get("entry_pos", [0, 0, 0]))
                exit_pos = tuple(arguments.get("exit_pos", [1000, 1000, 0]))
                url = arguments.get("url_tag", "TeleA")
                cmds = self.pathing_engine.generate_teleporter_pair(entry_pos=entry, exit_pos=exit_pos, url_tag=url)
                path_build_cmd = "PATHS DEFINE" if active_engine in ["ut2004", "ut2003"] else "PATHS BUILD"
                cmds.extend([path_build_cmd, "FLUSH"])
                results = self.controller.execute_batch(cmds)
                return {"status": "success", "teleporter": url}

            elif tool_name == "audit_pathing":
                log_lines = self.controller.get_log_deltas()
                report = self.pathing_engine.generate_reachability_report(log_lines)
                return {"status": "success", "audit_report": report}

            elif tool_name == "rebuild_level":
                build_paths = arguments.get("build_paths", True)
                cmds = ["MAP REBUILD", "LIGHT APPLY"]
                if build_paths:
                    path_cmd = "PATHS DEFINE" if active_engine in ["ut2004", "ut2003"] else "PATHS BUILD"
                    cmds.append(path_cmd)
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

            elif tool_name == "synthesize_mind_level":
                prompt = arguments.get("prompt", "")
                from .mind_synthesizer import MindSynthesizer
                cmds = MindSynthesizer.synthesize_level_from_mind(
                    prompt=prompt,
                    system_dir=self.controller.system_dir,
                    engine_id=active_engine,
                )
                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event(active_engine, "Mind-to-World Synthesis", f"{len(cmds)} cmds: {prompt[:40]}")
                self.memory_engine.record_build_event(active_engine, f"Mind Synthesis: {prompt[:30]}", len(cmds))
                return {"status": "success", "commands": len(cmds), "intent_prompt": prompt}

            elif tool_name == "generate_procedural_compound":
                room_count = int(arguments.get("room_count", 3))
                from .mind_synthesizer import MindSynthesizer
                cmds = MindSynthesizer.generate_procedural_compound(
                    room_count=room_count,
                    system_dir=self.controller.system_dir,
                    engine_id=active_engine,
                )
                results = self.controller.execute_batch(cmds)
                self.memory_engine.record_build_event(active_engine, f"Procedural Compound ({room_count} rooms)", len(cmds))
                return {"status": "success", "rooms": room_count, "commands": len(cmds)}

            elif tool_name == "distill_and_register_skill":
                s_name = arguments.get("skill_name", "CustomSkill")
                cat = arguments.get("category", "geometry")
                desc = arguments.get("description", "")
                params = arguments.get("parameters", {})
                from .skill_genesis import SkillGenesis
                genesis = SkillGenesis(self.memory_engine)
                ok = genesis.distill_and_register_skill(
                    skill_name=s_name,
                    category=cat,
                    description=desc,
                    parameters=params,
                    command_template=[],
                )
                return {"status": "success" if ok else "failed", "skill_name": s_name}

            elif tool_name == "wizard_build_level":
                preset = arguments.get("preset_key", "chizra_temple")
                crypt = arguments.get("include_secret_crypt", True)
                detail = arguments.get("detail_level", "ultra")
                from .wizard_builder import UnrealWizardBuilder
                cmds = UnrealWizardBuilder.build_unreal1_rpg_campaign_level(
                    preset_key=preset,
                    system_dir=self.controller.system_dir,
                    include_secret_crypt=crypt,
                    detail_level=detail,
                )
                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event(active_engine, "Wizard Build Level", f"{preset} ({len(cmds)} cmds)")
                self.memory_engine.record_build_event(active_engine, f"Wizard Level: {preset}", len(cmds))
                return {"status": "success", "preset": preset, "commands": len(cmds)}

            elif tool_name == "wizard_inject_extension":
                anchor = tuple(arguments.get("anchor_location", [0, 0, 0]))
                wing = arguments.get("wing_type", "secret_crypt")
                direction = arguments.get("direction", "North")
                from .wizard_builder import UnrealWizardBuilder
                cmds = UnrealWizardBuilder.inject_wing_into_existing_map(
                    anchor_location=anchor,
                    wing_type=wing,
                    direction=direction,
                    system_dir=self.controller.system_dir,
                    engine_id=active_engine,
                )
                results = self.controller.execute_batch(cmds)
                self.nexus_bridge.report_build_event(active_engine, "Wizard Inject Extension", f"{wing} ({direction})")
                self.memory_engine.record_build_event(active_engine, f"Injected Wing: {wing}", len(cmds))
                return {"status": "success", "wing_type": wing, "direction": direction, "commands": len(cmds)}

            elif tool_name == "query_unreal_academy":
                q = arguments.get("query", "")
                cat = arguments.get("category")
                from .learning_engine import LearningEngine
                academy = LearningEngine(self.memory_engine)
                entries = academy.query_academy(query=q, category=cat, limit=8)
                return {"status": "success", "query": q, "count": len(entries), "results": entries}

            elif tool_name == "ingest_master_insight":
                title = arguments.get("title", "")
                cat = arguments.get("category", "tips_and_tricks")
                summary = arguments.get("summary", "")
                steps = arguments.get("step_by_step", [])
                trick = arguments.get("technical_trick", "")
                from .learning_engine import LearningEngine
                academy = LearningEngine(self.memory_engine)
                ok = academy.ingest_knowledge_entry(
                    category=cat,
                    title=title,
                    summary=summary,
                    step_by_step=steps,
                    technical_trick=trick,
                    author_reference="Autonomous Agent Study",
                )
                return {"status": "success" if ok else "failed", "title": title}

            else:
                return {"status": "error", "error": f"Unknown tool '{tool_name}'"}

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def chat(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        artifacts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Dispatches a user query with dynamic memory RAG and native tool-calling schemas to active provider."""
        profile = self.config_mgr.get_active_llm_profile()
        provider = profile.get("provider", "google")
        model = profile.get("model", "gemini-2.5-flash")

        # Keep artifact paths out of the provider request until the selected
        # adapter supports multimodal parts. The UI records hashes locally and
        # includes a bounded manifest in the prompt for deterministic tools.

        system_prompt = self._build_system_prompt(user_query=user_message)
        normalized_artifacts = self._normalize_artifacts(artifacts or [], profile)
        logger.info(f"Dispatching chat to provider '{provider}' (Model: '{model}')")

        # Handle local offline Ollama / LM Studio or OpenAI-compatible
        if provider in ["openai", "openrouter", "groq", "deepseek", "ollama", "lmstudio"]:
            return self._chat_openai_compatible(user_message, history, profile, system_prompt, normalized_artifacts)
        elif provider == "anthropic":
            return self._chat_anthropic(user_message, history, profile, system_prompt, normalized_artifacts)
        else:
            # Default to Google Gemini
            return self._chat_gemini(user_message, history, profile, system_prompt, normalized_artifacts)

    @staticmethod
    def _normalize_artifacts(artifacts: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Returns bounded, provider-safe artifact metadata and payload data."""
        normalized: List[Dict[str, Any]] = []
        for artifact in artifacts[:8]:
            path = Path(str(artifact.get("path", "")))
            if not path.is_file() or path.stat().st_size > 8 * 1024 * 1024:
                continue
            entry = {"name": path.name, "kind": artifact.get("kind", "document"),
                     "size": path.stat().st_size, "sha256": artifact.get("sha256", "")}
            if entry["kind"] == "document":
                try:
                    entry["text"] = path.read_text(encoding="utf-8", errors="replace")[:20000]
                except OSError:
                    continue
            elif entry["kind"] in {"image", "viewport"} and profile.get("enable_vision", False):
                import base64
                entry["base64"] = base64.b64encode(path.read_bytes()).decode("ascii")
                entry["mime_type"] = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            if artifact.get("scene_graph_path"):
                try:
                    scene_graph = json.loads(Path(str(artifact["scene_graph_path"])).read_text(encoding="utf-8"))
                    names = [item.get("id", "") for item in scene_graph.get("landmarks", [])]
                    entry["text"] = "Reference scene graph landmarks: " + ", ".join(filter(None, names))
                except (OSError, json.JSONDecodeError):
                    pass
            normalized.append(entry)
        return normalized

    def test_provider_connection(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """Performs a bounded provider endpoint check without sending user content."""
        profile = self.config_mgr.get_all_llm_profiles().get(
            profile_id or self.config_mgr.get_active_llm_profile_id(), {}
        )
        provider = profile.get("provider", "")
        base_url = str(profile.get("base_url", "")).rstrip("/")
        api_key = profile.get("api_key", "")
        if provider in {"ollama", "lmstudio"}:
            url = f"{base_url}/models"
            headers = {}
        elif provider == "google":
            url = f"{base_url}/models?key={api_key}"
            headers = {}
        elif provider in {"openai", "openrouter", "groq", "deepseek"}:
            url = f"{base_url}/models"
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        else:
            return {"ok": bool(api_key), "provider": provider, "message": "Profile configured; provider-specific live check is unavailable."}
        try:
            request = Request(url, headers=headers, method="GET")
            with urlopen(request, timeout=8) as response:
                return {"ok": 200 <= response.status < 300, "provider": provider, "status": response.status, "message": "Endpoint reachable."}
        except Exception as exc:
            return {"ok": False, "provider": provider, "message": str(exc)}

    def _chat_openai_compatible(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]],
        profile: Dict[str, Any],
        system_prompt: str,
        artifacts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        base_url = profile.get("base_url", "https://api.openai.com/v1").rstrip("/")
        url = f"{base_url}/chat/completions"
        api_key = profile.get("api_key", "")
        model = profile.get("model", "gpt-4o")

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history[-8:]:
                messages.append(h)
        user_content: Any = user_message
        if artifacts:
            user_content = [{"type": "text", "text": user_message}]
            for artifact in artifacts:
                if "text" in artifact:
                    user_content.append({"type": "text", "text": f"\n[{artifact['name']}]\n{artifact['text']}"})
                elif "base64" in artifact:
                    user_content.append({"type": "image_url", "image_url": {"url": f"data:{artifact['mime_type']};base64,{artifact['base64']}"}})
        messages.append({"role": "user", "content": user_content})

        payload: Dict[str, Any] = {
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
        artifacts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        api_key = profile.get("api_key", "")
        model = profile.get("model", "gemini-2.5-flash")
        base_url = profile.get("base_url", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
        url = f"{base_url}/models/{model}:generateContent?key={api_key}"

        contents = []
        if history:
            for h in history[-6:]:
                role = "user" if h.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})
        parts: List[Dict[str, Any]] = [{"text": user_message}]
        for artifact in artifacts or []:
            if "text" in artifact:
                parts.append({"text": f"\n[{artifact['name']}]\n{artifact['text']}"})
            elif "base64" in artifact:
                parts.append({"inlineData": {"mimeType": artifact["mime_type"], "data": artifact["base64"]}})
        contents.append({"role": "user", "parts": parts})

        payload: Dict[str, Any] = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": profile.get("temperature", 0.2),
                "maxOutputTokens": profile.get("max_tokens", 8192),
            },
        }

        if profile.get("enable_tools", True):
            payload["tools"] = _tools_to_gemini_schema(UNREALED_TOOLS)

        try:
            req = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            candidates = data.get("candidates", [])
            if not candidates:
                return {"role": "assistant", "content": "No response received from Gemini.", "tool_executions": []}

            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = []
            executed_tools = []

            for p in parts:
                if "text" in p:
                    text_parts.append(p["text"])
                if "functionCall" in p:
                    fc = p["functionCall"]
                    name = fc.get("name", "")
                    args = fc.get("args", {})
                    res = self.execute_tool(name, args)
                    executed_tools.append({"tool": name, "args": args, "result": res})

            response_text = "".join(text_parts) if text_parts else ("Executed tools successfully." if executed_tools else "")
            return {"role": "assistant", "content": response_text, "tool_executions": executed_tools}

        except Exception as e:
            logger.error(f"Gemini request error: {e}")
            return {"role": "assistant", "content": f"⚠️ Gemini Error: {str(e)}", "tool_executions": []}

    def _chat_anthropic(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]],
        profile: Dict[str, Any],
        system_prompt: str,
        artifacts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        api_key = profile.get("api_key", "")
        model = profile.get("model", "claude-3-7-sonnet-20250219")
        url = "https://api.anthropic.com/v1/messages"

        messages = []
        if history:
            for h in history[-6:]:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        message_content: Any = user_message
        if artifacts:
            message_content = [{"type": "text", "text": user_message}]
            for artifact in artifacts:
                if "text" in artifact:
                    message_content.append({"type": "text", "text": f"\n[{artifact['name']}]\n{artifact['text']}"})
                elif "base64" in artifact:
                    message_content.append({"type": "image", "source": {"type": "base64", "media_type": artifact["mime_type"], "data": artifact["base64"]}})
        messages.append({"role": "user", "content": message_content})

        payload: Dict[str, Any] = {
            "model": model,
            "system": system_prompt,
            "messages": messages,
            "max_tokens": profile.get("max_tokens", 8192),
            "temperature": profile.get("temperature", 0.2),
        }

        if profile.get("enable_tools", True):
            payload["tools"] = _tools_to_anthropic_schema(UNREALED_TOOLS)

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
            text_parts = []
            executed_tools = []

            for b in content_blocks:
                b_type = b.get("type", "")
                if b_type == "text":
                    text_parts.append(b.get("text", ""))
                elif b_type == "tool_use":
                    name = b.get("name", "")
                    args = b.get("input", {})
                    res = self.execute_tool(name, args)
                    executed_tools.append({"tool": name, "args": args, "result": res})

            response_text = "".join(text_parts) if text_parts else ("Executed tools successfully." if executed_tools else "")
            return {"role": "assistant", "content": response_text, "tool_executions": executed_tools}

        except Exception as e:
            logger.error(f"Anthropic request error: {e}")
            return {"role": "assistant", "content": f"⚠️ Claude Error: {str(e)}", "tool_executions": []}

    def fetch_provider_models(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Connects to the configured provider API and retrieves the live list of available models.
        Returns {'ok': bool, 'models': List[str], 'message': str}.
        """
        pid = profile_id or self.config_mgr.get_active_llm_profile_id()
        prof = self.config_mgr.get_all_llm_profiles().get(pid, {})
        provider = prof.get("provider", "google").lower()
        api_key = prof.get("api_key", "").strip()
        base_url = prof.get("base_url", "").strip()

        fallback_models = {
            "google": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            "anthropic": ["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
            "openai": ["gpt-4o", "gpt-4o-mini", "o3-mini", "o1", "gpt-4-turbo", "gpt-3.5-turbo"],
            "ollama": ["qwen2.5-coder:32b", "llama3.3:70b", "deepseek-r1:32b", "mistral:7b", "codellama:34b"],
            "openrouter": ["google/gemini-2.5-flash", "anthropic/claude-3.7-sonnet", "deepseek/deepseek-r1", "openai/gpt-4o", "meta-llama/llama-3.3-70b-instruct"],
            "llamacpp": ["default", "local-model", "mistral-7b-instruct", "qwen2.5-coder-7b"],
            "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b"],
            "deepseek": ["deepseek-chat", "deepseek-reasoner"],
            "mistral": ["mistral-large-latest", "codestral-latest", "mistral-small-latest", "pixtral-large-latest"],
            "xai": ["grok-2-latest", "grok-2-vision-latest", "grok-beta"],
            "together": ["meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-Coder-32B-Instruct"],
            "fireworks": ["accounts/fireworks/models/llama-v3p3-70b-instruct", "accounts/fireworks/models/deepseek-v3", "accounts/fireworks/models/qwen2p5-coder-32b-instruct"],
            "cohere": ["command-r-plus-08-2024", "command-r-08-2024", "command-light"],
            "lmstudio": ["local-model", "qwen2.5-coder-7b-instruct", "meta-llama-3.1-8b-instruct"],
            "perplexity": ["sonar-pro", "sonar", "sonar-reasoning-pro"],
            "cerebras": ["llama3.3-70b", "llama3.1-8b"],
            "sambanova": ["Meta-Llama-3.3-70B-Instruct", "DeepSeek-R1", "Qwen2.5-Coder-32B-Instruct"],
            "ai21": ["jamba-1.5-large", "jamba-1.5-mini"],
            "cloudflare": ["@cf/meta/llama-3.3-70b-instruct", "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b"],
            "huggingface": ["meta-llama/Llama-3.3-70B-Instruct", "Qwen/Qwen2.5-Coder-32B-Instruct"],
            "custom": ["custom-model"],
        }

        # 1. Google Gemini Live Fetch
        if provider == "google":
            if not api_key:
                return {"ok": False, "models": fallback_models["google"], "message": "API key required to fetch Google Gemini models."}
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                req = Request(url, headers={"User-Agent": "UnrealAgentHarness"})
                with urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                models = []
                for m in data.get("models", []):
                    name = m.get("name", "").replace("models/", "")
                    if "gemini" in name:
                        models.append(name)
                models = sorted(models, reverse=True)
                return {"ok": True, "models": models or fallback_models["google"], "message": f"Successfully retrieved {len(models)} Gemini models from Google API."}
            except Exception as e:
                logger.warning(f"Google Gemini model fetch error: {e}")
                return {"ok": False, "models": fallback_models["google"], "message": f"Google Gemini API error ({e}). Using default list."}

        # 2. Local Ollama Live Fetch
        elif provider == "ollama":
            endpoint = base_url or "http://127.0.0.1:11434"
            tags_url = f"{endpoint.rstrip('/v1').rstrip('/')}/api/tags"
            try:
                req = Request(tags_url, headers={"User-Agent": "UnrealAgentHarness"})
                with urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                if models:
                    return {"ok": True, "models": models, "message": f"Found {len(models)} local Ollama model(s) installed."}
                return {"ok": True, "models": fallback_models["ollama"], "message": "Ollama connected (no models downloaded yet)."}
            except Exception as e:
                return {"ok": False, "models": fallback_models["ollama"], "message": f"Could not connect to Ollama at {tags_url}: {e}"}

        # 3. Anthropic Claude (Fixed Premier List)
        elif provider == "anthropic":
            if not api_key:
                return {"ok": False, "models": fallback_models["anthropic"], "message": "API key required for Anthropic Claude."}
            return {"ok": True, "models": fallback_models["anthropic"], "message": "Anthropic Claude catalog loaded (Sonnet 4, 3.7 Sonnet, 3.5 Sonnet, 3.5 Haiku)."}

        # 4. Universal OpenAI-Compatible Fetch (OpenAI, OpenRouter, llama.cpp, Groq, DeepSeek, Mistral, xAI, Together, Fireworks, Cohere, LM Studio, Perplexity, Cerebras, SambaNova, AI21, Cloudflare, HuggingFace, Custom)
        else:
            default_urls = {
                "openai": "https://api.openai.com/v1",
                "openrouter": "https://openrouter.ai/api/v1",
                "llamacpp": "http://127.0.0.1:8080/v1",
                "groq": "https://api.groq.com/openai/v1",
                "deepseek": "https://api.deepseek.com/v1",
                "mistral": "https://api.mistral.ai/v1",
                "xai": "https://api.x.ai/v1",
                "together": "https://api.together.xyz/v1",
                "fireworks": "https://api.fireworks.ai/inference/v1",
                "cohere": "https://api.cohere.com/v2",
                "lmstudio": "http://127.0.0.1:1234/v1",
                "perplexity": "https://api.perplexity.ai",
                "cerebras": "https://api.cerebras.ai/v1",
                "sambanova": "https://api.sambanova.ai/v1",
                "ai21": "https://api.ai21.com/studio/v1",
                "cloudflare": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
                "huggingface": "https://api-inference.huggingface.co/v1",
                "custom": "http://127.0.0.1:8000/v1",
            }

            active_base = base_url or default_urls.get(provider, "http://127.0.0.1:8000/v1")
            endpoint = f"{active_base.rstrip('/')}/models"

            headers = {"User-Agent": "UnrealAgentHarness"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            try:
                req = Request(endpoint, headers=headers)
                with urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                raw_data = data.get("data", []) or data.get("models", [])
                models = []
                for item in raw_data:
                    if isinstance(item, dict):
                        m_id = item.get("id") or item.get("name", "")
                        if m_id:
                            models.append(m_id)
                    elif isinstance(item, str):
                        models.append(item)

                if models:
                    return {"ok": True, "models": sorted(models[:60]), "message": f"Successfully retrieved {len(models)} models from {provider} API."}
            except Exception as e:
                logger.debug(f"{provider} model query note: {e}")

            return {"ok": True, "models": f_list, "message": f"{provider.capitalize()} catalog loaded ({len(f_list)} suggested models)."}
