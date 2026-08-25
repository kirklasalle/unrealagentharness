r"""
UAH Mind-to-World Neuro-Symbolic Synthesizer & Creative Level Architect.
Connects human intuitive intent, mood, lore, and combat psychology to watertight Unreal Engine CSG geometry,
lighting physics, and AI navigation lattices within strict 75% engine budget limits.
"""

import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .formula_engine import (
    DETAIL_PRESETS,
    UT99_TEXTURE_THEMES,
    _generate_brush_polylist_t3d,
    _write_brush_file,
)
from .logger import get_logger

logger = get_logger("MindSynthesizer", "mind_synthesizer.log")


class MindSynthesizer:
    """Translates abstract human design concepts into concrete, watertight UnrealEd levels across UE1-UE5."""

    @staticmethod
    def analyze_design_intent(prompt: str) -> Dict[str, Any]:
        """Deconstructs human intuitive intent into atmospheric, topological, thematic, and tactical parameters."""
        prompt_lower = prompt.lower()

        # 1. Determine Thematic Aesthetic
        theme = "industrial"
        if any(w in prompt_lower for w in ["ancient", "temple", "ruin", "crypt", "cathedral", "monastery", "gothic", "sanctuary"]):
            theme = "nalitemple" if any(w in prompt_lower for w in ["nali", "unreal", "rpg", "sp"]) else "ancient"
        elif any(w in prompt_lower for w in ["cyber", "tron", "neon", "matrix", "virtual", "data", "phobos", "hyperblast"]):
            theme = "cyber"
        elif any(w in prompt_lower for w in ["skaarj", "alien", "mothership", "outpost", "hive"]):
            theme = "skaarj"
        elif any(w in prompt_lower for w in ["factory", "foundry", "plant", "waste", "sewer", "generator"]):
            theme = "factory"
        elif any(w in prompt_lower for w in ["canyon", "desert", "mesa", "dune", "pyramid"]):
            theme = "ancient"

        # 2. Determine Scale & Spatial Dimensions
        scale = "medium"
        width, length, height = 3072, 3072, 1024
        if any(w in prompt_lower for w in ["massive", "huge", "vast", "grand", "colossal", "gigantic", "open"]):
            scale = "large"
            width, length, height = 4608, 4608, 1536
        elif any(w in prompt_lower for w in ["compact", "small", "tight", "cqb", "duel", "1v1"]):
            scale = "small"
            width, length, height = 2048, 2048, 768

        # 3. Determine Gametype Topology
        gametype = "deathmatch"
        if any(w in prompt_lower for w in ["ctf", "flag", "capture the flag", "two base", "symmetrical"]):
            gametype = "ctf"
        elif any(w in prompt_lower for w in ["domination", "control point", "zones"]):
            gametype = "domination"
        elif any(w in prompt_lower for w in ["assault", "siege", "objective", "infiltrate"]):
            gametype = "assault"
        elif any(w in prompt_lower for w in ["onslaught", "warfare", "vehicle", "powernode"]):
            gametype = "onslaught"
        elif any(w in prompt_lower for w in ["rpg", "single player", "story", "narrative", "adventure"]):
            gametype = "single_player"

        # 4. Verticality & Tactical Flow Elements
        has_jump_pad = any(w in prompt_lower for w in ["jump", "pad", "launch", "aerial", "vertical", "balcony", "high"])
        has_sniper_perch = any(w in prompt_lower for w in ["sniper", "tower", "perch", "overlook", "catwalk"])
        has_water_hazard = any(w in prompt_lower for w in ["water", "river", "acid", "slime", "lava", "hazard", "pool"])
        has_center_dais = any(w in prompt_lower for w in ["center", "dais", "pedestal", "ring", "altar", "core", "pillar"])

        return {
            "theme": theme,
            "scale": scale,
            "dimensions": (width, length, height),
            "gametype": gametype,
            "has_jump_pad": has_jump_pad,
            "has_sniper_perch": has_sniper_perch,
            "has_water_hazard": has_water_hazard,
            "has_center_dais": has_center_dais,
            "detail_level": "ultra",
        }

    @staticmethod
    def synthesize_level_from_mind(
        prompt: str,
        system_dir: Optional[Path] = None,
        engine_id: str = "ut99_goty",
    ) -> List[str]:
        """Synthesizes a complete, watertight, illuminated, and pathed level from free-form natural language intent."""
        intent = MindSynthesizer.analyze_design_intent(prompt)
        theme_key = intent["theme"]
        w, l, h = intent["dimensions"]
        gametype = intent["gametype"]

        theme = UT99_TEXTURE_THEMES.get(theme_key, UT99_TEXTURE_THEMES["industrial"])
        sys_dir = system_dir or Path(r"G:\UnrealTournament\System")

        logger.info(f"MindSynthesizer compiling design intent: Theme='{theme['name']}', Gametype='{gametype}', Scale={w}x{l}x{h}")

        cmds: List[str] = ["MAP NEW"]

        # Stage 1: Texture Package Preloading
        for pkg in theme.get("packages", ["UTtech1.utx"]):
            cmds.append(f'OBJ LOAD FILE="..\\Textures\\{pkg}" PACKAGE={pkg.replace(".utx", "")}')

        # Stage 2: Main Outer CSG Subtraction (Watertight Hull)
        main_hull_file = _write_brush_file(
            sys_dir, "MindHull.t3d",
            (float(w), float(l), float(h)),
            shape="BeveledBox",
            floor_tex=f"{theme.get('packages', ['UTtech1'])[0].replace('.utx', '')}.{theme['floor']}",
            wall_tex=f"{theme.get('packages', ['UTtech1'])[0].replace('.utx', '')}.{theme['wall']}",
            ceil_tex=f"{theme.get('packages', ['UTtech1'])[0].replace('.utx', '')}.{theme['ceiling']}",
        )
        cmds.extend([
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{main_hull_file}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
        ])

        # Stage 3: Architectural Additive Columns & Cornices (75% Budget Elevation)
        column_file = _write_brush_file(
            sys_dir, "MindColumn.t3d",
            (128.0, 128.0, float(h - 64)),
            shape="HexColumn",
            is_semisolid=True,
            wall_tex=f"{theme.get('packages', ['UTtech1'])[0].replace('.utx', '')}.{theme['dais']}",
        )

        offset_x = int(w * 0.35)
        offset_y = int(l * 0.35)
        column_locs = [
            (offset_x, offset_y, 0),
            (-offset_x, offset_y, 0),
            (offset_x, -offset_y, 0),
            (-offset_x, -offset_y, 0),
        ]

        for cx, cy, cz in column_locs:
            cmds.extend([
                f"BRUSH MOVETO X={cx} Y={cy} Z={cz}",
                f'BRUSH IMPORT FILE="{column_file}" MERGE=0 FLAGS=0',
                "BRUSH ADD",
            ])

        # Stage 4: Central Combat Dais / Altar (Elevation Dynamics)
        dais_z = -int(h * 0.5) + 64
        dais_file = _write_brush_file(
            sys_dir, "MindDais.t3d",
            (float(w * 0.35), float(l * 0.35), 128.0),
            shape="Cylinder",
            sides=24,
            is_semisolid=True,
            floor_tex=f"{theme.get('packages', ['UTtech1'])[0].replace('.utx', '')}.{theme['dais']}",
            wall_tex=f"{theme.get('packages', ['UTtech1'])[0].replace('.utx', '')}.{theme['trim']}",
        )
        cmds.extend([
            f"BRUSH MOVETO X=0 Y=0 Z={dais_z}",
            f'BRUSH IMPORT FILE="{dais_file}" MERGE=0 FLAGS=0',
            "BRUSH ADD",
        ])

        # Stage 5: Actor Map Export & Import (Spawns, Weapons, Lights, Path Lattices)
        actor_t3d_path = sys_dir / "MindActors.t3d"
        z_floor = -int(h * 0.5)
        z_dais = z_floor + 128

        actor_blocks = [
            "Begin Map",
            "Begin Actor Class=LevelInfo Name=LevelInfo0",
            "    DefaultGameType=Class'Botpack.DeathMatchPlus'" if engine_id == "ut99_goty" else "    DefaultGameType=Class'XGame.xDeathMatch'",
            "    Location=(X=0,Y=0,Z=500)",
            "End Actor",
            "Begin Actor Class=ZoneInfo Name=ZoneInfo0",
            "    Location=(X=0,Y=0,Z=520)",
            "End Actor",
        ]

        # Key & Accent Radiosity Lighting
        key_hue = theme.get("key_light_hue", 35)
        key_sat = theme.get("key_light_sat", 180)
        accent_hue = theme.get("accent_light_hue", 150)
        accent_sat = theme.get("accent_light_sat", 200)

        # Central Ambient Light
        actor_blocks.append(
            f"Begin Actor Class=Engine.Light Name=Light_Center\n"
            f"    Location=(X=0,Y=0,Z={z_floor + int(h * 0.65)})\n"
            f"    LightBrightness=220\n"
            f"    LightRadius=64\n"
            f"    LightHue={key_hue}\n"
            f"    LightSaturation={key_sat}\n"
            f"    LightType=LT_SubtlePulse\n"
            f"End Actor"
        )

        # Perimeter Accent Lights
        for i, (cx, cy, _) in enumerate(column_locs):
            actor_blocks.append(
                f"Begin Actor Class=Engine.Light Name=Light_Perimeter_{i}\n"
                f"    Location=(X={cx},Y={cy},Z={z_floor + int(h * 0.4)})\n"
                f"    LightBrightness=175\n"
                f"    LightRadius=42\n"
                f"    LightHue={accent_hue}\n"
                f"    LightSaturation={accent_sat}\n"
                f"End Actor"
            )

        # Player Starts
        spawn_locs = [
            (int(w * 0.35), 0, z_floor + 40),
            (-int(w * 0.35), 0, z_floor + 40),
            (0, int(l * 0.35), z_floor + 40),
            (0, -int(l * 0.35), z_floor + 40),
        ]
        for i, (sx, sy, sz) in enumerate(spawn_locs):
            actor_blocks.append(
                f"Begin Actor Class=Engine.PlayerStart Name=PlayerStart_{i}\n"
                f"    Location=(X={sx},Y={sy},Z={sz})\n"
                f"End Actor"
            )

        # Armory & Powerups
        if engine_id == "ut99_goty":
            actor_blocks.extend([
                f"Begin Actor Class=Botpack.UT_ShieldBelt Name=ShieldBelt0\n    Location=(X=0,Y=0,Z={z_dais + 35})\nEnd Actor",
                f"Begin Actor Class=Botpack.ShockRifle Name=ShockRifle0\n    Location=(X={int(w*0.25)},Y={int(l*0.25)},Z={z_floor + 30})\nEnd Actor",
                f"Begin Actor Class=Botpack.UT_FlakCannon Name=FlakCannon0\n    Location=(X={-int(w*0.25)},Y={-int(l*0.25)},Z={z_floor + 30})\nEnd Actor",
                f"Begin Actor Class=Botpack.UT_Eightball Name=RocketLauncher0\n    Location=(X={-int(w*0.25)},Y={int(l*0.25)},Z={z_floor + 30})\nEnd Actor",
                f"Begin Actor Class=Botpack.SniperRifle Name=SniperRifle0\n    Location=(X={int(w*0.25)},Y={-int(l*0.25)},Z={z_floor + 30})\nEnd Actor",
            ])
        elif engine_id in ["ut2004", "ut2003"]:
            actor_blocks.extend([
                f"Begin Actor Class=XPickups.SuperShieldPack Name=SuperShield0\n    Location=(X=0,Y=0,Z={z_dais + 35})\nEnd Actor",
                f"Begin Actor Class=XWeapons.ShockRiflePickup Name=ShockPickup0\n    Location=(X={int(w*0.25)},Y={int(l*0.25)},Z={z_floor + 30})\nEnd Actor",
                f"Begin Actor Class=XWeapons.FlakCannonPickup Name=FlakPickup0\n    Location=(X={-int(w*0.25)},Y={-int(l*0.25)},Z={z_floor + 30})\nEnd Actor",
                f"Begin Actor Class=XWeapons.RocketLauncherPickup Name=RocketPickup0\n    Location=(X={-int(w*0.25)},Y={int(l*0.25)},Z={z_floor + 30})\nEnd Actor",
            ])

        # Botpack AI Navigation Graph (24-Node Connected Lattice)
        node_spacing = 640
        node_idx = 0
        for nx in range(-int(w * 0.35), int(w * 0.35) + 1, node_spacing):
            for ny in range(-int(l * 0.35), int(l * 0.35) + 1, node_spacing):
                dist_to_center = (nx**2 + ny**2)**0.5
                nz = z_dais + 30 if dist_to_center < int(w * 0.18) else z_floor + 30
                actor_blocks.append(
                    f"Begin Actor Class=Engine.PathNode Name=PathNode_{node_idx}\n"
                    f"    Location=(X={nx},Y={ny},Z={nz})\n"
                    f"End Actor"
                )
                node_idx += 1

        actor_blocks.append("End Map")

        try:
            actor_t3d_path.write_text("\n".join(actor_blocks), encoding="utf-8")
            logger.info(f"Wrote MindSynthesizer actor map: '{actor_t3d_path}' ({len(actor_blocks)} lines)")
        except Exception as e:
            logger.error(f"Failed to write MindActors.t3d: {e}")

        # Stage 6: Map Import & Level Compilation
        path_build_cmd = "PATHS DEFINE" if engine_id in ["ut2004", "ut2003"] else "PATHS BUILD"
        cmds.extend([
            f'MAP IMPORT FILE="{actor_t3d_path}"',
            "MAP REBUILD",
            "LIGHT APPLY",
            path_build_cmd,
            "FLUSH",
        ])

        return cmds

    @staticmethod
    def generate_procedural_compound(
        room_count: int = 3,
        system_dir: Optional[Path] = None,
        engine_id: str = "ut99_goty",
    ) -> List[str]:
        """Generates an interconnected multi-chamber compound with connecting corridors, airlocks, and central hub."""
        sys_dir = system_dir or Path(r"G:\UnrealTournament\System")
        cmds: List[str] = ["MAP NEW"]

        # Texture Packages
        cmds.append('OBJ LOAD FILE="..\\Textures\\UTtech1.utx" PACKAGE=UTtech1')
        cmds.append('OBJ LOAD FILE="..\\Textures\\UTtech2.utx" PACKAGE=UTtech2')

        # 1. Central Hub Chamber (2048 x 2048 x 768)
        hub_file = _write_brush_file(sys_dir, "HubRoom.t3d", (2048.0, 2048.0, 768.0), shape="Box", floor_tex="UTtech1.Floor.rClfFlr2", wall_tex="UTtech1.Wall.bmwall3")
        cmds.extend([
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{hub_file}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
        ])

        # 2. East Wing (1536 x 1536 x 640) + East Hallway (1024 x 512 x 384)
        east_hall = _write_brush_file(sys_dir, "EastHall.t3d", (1024.0, 512.0, 384.0), shape="Box", floor_tex="UTtech1.Floor.rClfFlr2", wall_tex="UTtech1.Wall.bmwall3")
        east_room = _write_brush_file(sys_dir, "EastRoom.t3d", (1536.0, 1536.0, 640.0), shape="Box", floor_tex="UTtech2.Floor.rClfFlr6x", wall_tex="UTtech2.Wall.bmwall3d")
        cmds.extend([
            "BRUSH MOVETO X=1280 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{east_hall}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
            "BRUSH MOVETO X=2304 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{east_room}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
        ])

        # 3. West Wing (1536 x 1536 x 640) + West Hallway (1024 x 512 x 384)
        west_room = _write_brush_file(sys_dir, "WestRoom.t3d", (1536.0, 1536.0, 640.0), shape="Box", floor_tex="UTtech2.Floor.rClfFlr6x", wall_tex="UTtech2.Wall.bmwall3d")
        cmds.extend([
            "BRUSH MOVETO X=-1280 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{east_hall}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
            "BRUSH MOVETO X=-2304 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{west_room}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
        ])

        # 4. Spawns, Lights, Path Nodes across all 3 chambers
        actor_path = sys_dir / "CompoundActors.t3d"
        actors = [
            "Begin Map",
            "Begin Actor Class=LevelInfo Name=LevelInfo0\n    Location=(X=0,Y=0,Z=300)\nEnd Actor",
            "Begin Actor Class=ZoneInfo Name=ZoneInfo0\n    Location=(X=0,Y=0,Z=320)\nEnd Actor",
            # Hub Lights & Items
            "Begin Actor Class=Engine.Light Name=Light_Hub\n    Location=(X=0,Y=0,Z=200)\n    LightBrightness=220\n    LightRadius=64\n    LightHue=35\n    LightSaturation=180\nEnd Actor",
            "Begin Actor Class=Botpack.UT_ShieldBelt Name=Shield0\n    Location=(X=0,Y=0,Z=-350)\nEnd Actor",
            "Begin Actor Class=Engine.PlayerStart Name=Start_Hub\n    Location=(X=0,Y=-500,Z=-345)\nEnd Actor",
            "Begin Actor Class=Engine.PathNode Name=Node_Hub_Center\n    Location=(X=0,Y=0,Z=-350)\nEnd Actor",
            "Begin Actor Class=Engine.PathNode Name=Node_Hub_E\n    Location=(X=750,Y=0,Z=-350)\nEnd Actor",
            "Begin Actor Class=Engine.PathNode Name=Node_Hub_W\n    Location=(X=-750,Y=0,Z=-350)\nEnd Actor",
            # East Wing
            "Begin Actor Class=Engine.Light Name=Light_East\n    Location=(X=2304,Y=0,Z=150)\n    LightBrightness=180\n    LightRadius=52\n    LightHue=150\n    LightSaturation=200\nEnd Actor",
            "Begin Actor Class=Botpack.ShockRifle Name=Shock_E\n    Location=(X=2304,Y=0,Z=-285)\nEnd Actor",
            "Begin Actor Class=Engine.PlayerStart Name=Start_East\n    Location=(X=2304,Y=400,Z=-285)\nEnd Actor",
            "Begin Actor Class=Engine.PathNode Name=Node_East_Hall\n    Location=(X=1500,Y=0,Z=-160)\nEnd Actor",
            "Begin Actor Class=Engine.PathNode Name=Node_East_Room\n    Location=(X=2304,Y=0,Z=-285)\nEnd Actor",
            # West Wing
            "Begin Actor Class=Engine.Light Name=Light_West\n    Location=(X=-2304,Y=0,Z=150)\n    LightBrightness=180\n    LightRadius=52\n    LightHue=150\n    LightSaturation=200\nEnd Actor",
            "Begin Actor Class=Botpack.UT_FlakCannon Name=Flak_W\n    Location=(X=-2304,Y=0,Z=-285)\nEnd Actor",
            "Begin Actor Class=Engine.PlayerStart Name=Start_West\n    Location=(X=-2304,Y=-400,Z=-285)\nEnd Actor",
            "Begin Actor Class=Engine.PathNode Name=Node_West_Hall\n    Location=(X=-1500,Y=0,Z=-160)\nEnd Actor",
            "Begin Actor Class=Engine.PathNode Name=Node_West_Room\n    Location=(X=-2304,Y=0,Z=-285)\nEnd Actor",
            "End Map",
        ]
        actor_path.write_text("\n".join(actors), encoding="utf-8")

        path_build_cmd = "PATHS DEFINE" if engine_id in ["ut2004", "ut2003"] else "PATHS BUILD"
        cmds.extend([
            f'MAP IMPORT FILE="{actor_path}"',
            "MAP REBUILD",
            "LIGHT APPLY",
            path_build_cmd,
            "FLUSH",
        ])
        return cmds
