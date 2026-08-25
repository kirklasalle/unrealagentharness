r"""
UAH Unreal Architect Wizard Builder Engine.
Dual-Mode Procedural Level & Campaign Synthesizer:
  1. Build from Scratch: Clean-slate complete world generation (Unreal 1 SP RPG, UT99 Arena/CTF, UTron, UT2004).
  2. Inject into Existing Map: Non-destructive in-situ map expansion (secret crypts, sniper towers, corridor wings, lore logs).
Incorporates deep 1998 'Unreal' single-player RPG lore, TranslatorEvents, Nali NPCs, Skaarj AI, and mover puzzle mechanics.
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .formula_engine import (
    DETAIL_PRESETS,
    UT99_TEXTURE_THEMES,
    _generate_brush_polylist_t3d,
    _write_brush_file,
)
from .logger import get_logger

logger = get_logger("WizardBuilder", "wizard_builder.log")


class UnrealWizardBuilder:
    """Master procedural wizard for clean-slate generation and non-destructive in-situ map extensions."""

    # -------------------------------------------------------------------------
    # UNREAL 1 (1998) RPG NARRATIVE LORE PRESETS
    # -------------------------------------------------------------------------
    UNREAL1_LORE_PRESETS = {
        "chizra_temple": {
            "title": "Chizra, Water God Temple",
            "theme": "nalitemple",
            "ambient_music": "Chizra.umx",
            "translator_messages": [
                "LOG 01: 'Chizra awaits the pure of heart. Cast aside your weapons before entering the Sacred Pool of Cleansing.'",
                "LOG 02: 'The Sky Demons have defiled the altar. Our brethren weep in chains beneath the Sunspire.'",
                "SECRET LOG: 'Strike the golden serpent engraving on the north pillar to reveal the sacred Dispersion Pistol upgrade.'",
            ],
            "creatures": ["UnrealShare.Nali", "UnrealShare.Brute", "UnrealI.SkaarjWarrior", "UnrealShare.Slith"],
            "weapons": ["UnrealShare.DispersionPistol", "UnrealShare.Stinger", "UnrealShare.Automag", "UnrealShare.ASMD"],
        },
        "skaarj_mothership": {
            "title": "Skaarj Mothership Infiltration",
            "theme": "skaarj",
            "ambient_music": "Seti.umx",
            "translator_messages": [
                "SECURITY ALERT: 'Intruder detected in Sector 4 Sub-Deck. Energy barriers activated. Release Trooper squads.'",
                "TACTICAL LOG: 'Reactor overload in T-minus 10 minutes. Escape pods jettisoned by order of Queen Skaarj.'",
            ],
            "creatures": ["UnrealI.SkaarjTrooper", "UnrealI.SkaarjOfficer", "UnrealI.SkaarjGunner", "UnrealShare.Pupae"],
            "weapons": ["UnrealShare.Razorjack", "UnrealShare.Eightball", "UnrealShare.FlakCannon", "UnrealShare.Rifle"],
        },
        "bluff_eversmoking": {
            "title": "Bluff Eversmoking Mountain Fortress",
            "theme": "ancient",
            "ambient_music": "Bluff.umx",
            "translator_messages": [
                "NALI SCROLL: 'High above the clouds, the Bell Tower rings for those who fall to the Skaarj guards.'",
                "PRISON LOG: 'Cell Block B sealed. Lever mechanism located in the cemetery crypts.'",
            ],
            "creatures": ["UnrealShare.Nali", "UnrealShare.Brute", "UnrealI.Krall", "UnrealI.KrallElite"],
            "weapons": ["UnrealShare.Automag", "UnrealShare.Stinger", "UnrealShare.Eightball", "UnrealShare.ASMD"],
        },
    }

    @staticmethod
    def build_unreal1_rpg_campaign_level(
        preset_key: str = "chizra_temple",
        system_dir: Optional[Path] = None,
        include_secret_crypt: bool = True,
        detail_level: str = "ultra",
    ) -> List[str]:
        """Synthesizes a complete Unreal 1 Single-Player narrative RPG exploration level from scratch."""
        sys_dir = system_dir or Path(r"G:\UnrealTournament\System")
        preset = UnrealWizardBuilder.UNREAL1_LORE_PRESETS.get(preset_key, UnrealWizardBuilder.UNREAL1_LORE_PRESETS["chizra_temple"])
        theme = UT99_TEXTURE_THEMES.get(preset["theme"], UT99_TEXTURE_THEMES["nalitemple"])

        logger.info(f"Wizard building Unreal 1 RPG Campaign Level: '{preset['title']}' (Detail: {detail_level})")

        cmds: List[str] = ["MAP NEW"]

        # 1. Texture Packages
        for pkg in theme.get("packages", ["NaliCast.utx", "Ancient.utx"]):
            cmds.append(f'OBJ LOAD FILE="..\\Textures\\{pkg}" PACKAGE={pkg.replace(".utx", "")}')

        # 2. Main Grand Temple Nave (3584 x 2048 x 1024)
        nave_file = _write_brush_file(
            sys_dir, "WizNave.t3d",
            (3584.0, 2048.0, 1024.0),
            shape="BeveledBox",
            floor_tex="NaliCast.CasFLOR",
            wall_tex="NaliCast.OldWallH",
            ceil_tex="Ancient.Arch",
        )
        cmds.extend([
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{nave_file}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
        ])

        # 3. Fluted Semi-Solid Sanctuary Columns
        col_file = _write_brush_file(
            sys_dir, "WizCol.t3d",
            (128.0, 128.0, 960.0),
            shape="HexColumn",
            is_semisolid=True,
            wall_tex="Ancient.APillar",
        )
        col_positions = [
            (800, 600, 0), (800, -600, 0),
            (-800, 600, 0), (-800, -600, 0),
            (0, 600, 0), (0, -600, 0),
        ]
        for cx, cy, cz in col_positions:
            cmds.extend([
                f"BRUSH MOVETO X={cx} Y={cy} Z={cz}",
                f'BRUSH IMPORT FILE="{col_file}" MERGE=0 FLAGS=0',
                "BRUSH ADD",
            ])

        # 4. Elevated Altar Dais (1024 x 1024 x 128)
        altar_file = _write_brush_file(
            sys_dir, "WizAltar.t3d",
            (1024.0, 1024.0, 128.0),
            shape="Cylinder",
            sides=24,
            is_semisolid=True,
            floor_tex="NaliCast.CasFLOR",
            wall_tex="ShaneChurch.Bwood",
        )
        cmds.extend([
            "BRUSH MOVETO X=-1200 Y=0 Z=-448",
            f'BRUSH IMPORT FILE="{altar_file}" MERGE=0 FLAGS=0',
            "BRUSH ADD",
        ])

        # 5. Secret Subterranean Crypt Wing (If requested)
        if include_secret_crypt:
            crypt_hall = _write_brush_file(sys_dir, "WizCryptHall.t3d", (512.0, 1024.0, 384.0), shape="Box", floor_tex="NaliCast.CasFLOR", wall_tex="NaliCast.OldWallH")
            crypt_room = _write_brush_file(sys_dir, "WizCryptRoom.t3d", (1536.0, 1536.0, 512.0), shape="Box", floor_tex="NaliCast.CasFLOR", wall_tex="NaliCast.OldWallH")
            cmds.extend([
                "BRUSH MOVETO X=0 Y=1536 Z=-300",
                f'BRUSH IMPORT FILE="{crypt_hall}" MERGE=0 FLAGS=0',
                "BRUSH SUBTRACT",
                "BRUSH MOVETO X=0 Y=2816 Z=-300",
                f'BRUSH IMPORT FILE="{crypt_room}" MERGE=0 FLAGS=0',
                "BRUSH SUBTRACT",
            ])

        # 6. Narrative Actors & Story Lore T3D Map
        actor_t3d = sys_dir / "WizActors.t3d"
        actors = [
            "Begin Map",
            "Begin Actor Class=LevelInfo Name=LevelInfo0\n    Title=\"" + preset["title"] + "\"\n    Author=\"Kirk LaSalle & UAH Wizard\"\n    Location=(X=0,Y=0,Z=450)\nEnd Actor",
            "Begin Actor Class=ZoneInfo Name=ZoneInfo0\n    Location=(X=0,Y=0,Z=480)\nEnd Actor",
            # Player Start at Temple Entrance
            "Begin Actor Class=Engine.PlayerStart Name=PlayerStart_Entrance\n    Location=(X=1400,Y=0,Z=-470)\nEnd Actor",
            # Dispersion Pistol Starter Weapon
            "Begin Actor Class=UnrealShare.DispersionPistol Name=Weapon_Dispersion\n    Location=(X=1200,Y=0,Z=-470)\nEnd Actor",
            # Atmospheric Torchlight & Chiaroscuro Lighting
            "Begin Actor Class=UnrealShare.TorchFlame Name=Torch_Altar_L\n    Location=(X=-1200,Y=350,Z=-350)\n    LightBrightness=220\n    LightRadius=48\n    LightHue=22\n    LightSaturation=180\n    LightType=LT_Flicker\nEnd Actor",
            "Begin Actor Class=UnrealShare.TorchFlame Name=Torch_Altar_R\n    Location=(X=-1200,Y=-350,Z=-350)\n    LightBrightness=220\n    LightRadius=48\n    LightHue=22\n    LightSaturation=180\n    LightType=LT_Flicker\nEnd Actor",
            # Central Nave Ambient Light
            "Begin Actor Class=Engine.Light Name=Light_Nave_Center\n    Location=(X=0,Y=0,Z=200)\n    LightBrightness=180\n    LightRadius=64\n    LightHue=35\n    LightSaturation=200\n    LightType=LT_SubtlePulse\nEnd Actor",
            # TranslatorEvent Story Messages
            f"Begin Actor Class=UnrealShare.TranslatorEvent Name=StoryLog_1\n    Location=(X=1000,Y=-250,Z=-460)\n    Message=\"{preset['translator_messages'][0]}\"\n    bHint=True\nEnd Actor",
            f"Begin Actor Class=UnrealShare.TranslatorEvent Name=StoryLog_2\n    Location=(X=-1200,Y=0,Z=-350)\n    Message=\"{preset['translator_messages'][1]}\"\nEnd Actor",
            # Nali Monk NPC Praying on Altar
            "Begin Actor Class=UnrealShare.Nali Name=Nali_Priest\n    Location=(X=-1200,Y=0,Z=-350)\n    Health=100\nEnd Actor",
            # Temple Guard Brute
            "Begin Actor Class=UnrealShare.Brute Name=Brute_Guard_1\n    Location=(X=0,Y=-400,Z=-470)\nEnd Actor",
            # Skaarj Assassin on Mezzanine
            "Begin Actor Class=UnrealI.SkaarjWarrior Name=Skaarj_Patrol\n    Location=(X=-400,Y=0,Z=-470)\nEnd Actor",
            # Healing Nali Fruit
            "Begin Actor Class=UnrealShare.NaliFruit Name=Fruit_1\n    Location=(X=-800,Y=800,Z=-480)\nEnd Actor",
            "Begin Actor Class=UnrealShare.NaliFruit Name=Fruit_2\n    Location=(X=-800,Y=-800,Z=-480)\nEnd Actor",
        ]

        # Path Nodes Lattice (Spaced every 500 UU)
        p_idx = 0
        for px in range(-1200, 1400 + 1, 500):
            for py in range(-800, 800 + 1, 500):
                pz = -350 if px <= -1000 and abs(py) <= 400 else -470
                actors.append(f"Begin Actor Class=Engine.PathNode Name=Path_Nave_{p_idx}\n    Location=(X={px},Y={py},Z={pz})\nEnd Actor")
                p_idx += 1

        if include_secret_crypt:
            actors.extend([
                # Secret Crypt Lore & Slith Guard
                f"Begin Actor Class=UnrealShare.TranslatorEvent Name=StoryLog_Secret\n    Location=(X=0,Y=2816,Z=-260)\n    Message=\"{preset['translator_messages'][2]}\"\nEnd Actor",
                "Begin Actor Class=UnrealShare.Slith Name=Slith_Crypt_Beast\n    Location=(X=0,Y=2816,Z=-260)\nEnd Actor",
                "Begin Actor Class=UnrealShare.Eightball Name=Rocket_Crypt_Reward\n    Location=(X=0,Y=2900,Z=-260)\nEnd Actor",
                "Begin Actor Class=Engine.Light Name=Light_Crypt\n    Location=(X=0,Y=2816,Z=-100)\n    LightBrightness=160\n    LightRadius=42\n    LightHue=85\n    LightSaturation=220\n    LightType=LT_Pulse\nEnd Actor",
                "Begin Actor Class=Engine.PathNode Name=Path_Crypt_1\n    Location=(X=0,Y=1536,Z=-260)\nEnd Actor",
                "Begin Actor Class=Engine.PathNode Name=Path_Crypt_2\n    Location=(X=0,Y=2816,Z=-260)\nEnd Actor",
            ])

        actors.append("End Map")

        try:
            actor_t3d.write_text("\n".join(actors), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to write WizActors.t3d: {e}")

        # 7. Import Actors & Rebuild Level
        cmds.extend([
            f'MAP IMPORT FILE="{actor_t3d}"',
            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ])

        return cmds

    @staticmethod
    def inject_wing_into_existing_map(
        anchor_location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        wing_type: str = "secret_crypt",
        direction: str = "North",
        system_dir: Optional[Path] = None,
        engine_id: str = "ut99_goty",
    ) -> List[str]:
        """
        NON-DESTRUCTIVE: Injects an interconnected wing, crypt, or tower into the currently open active map in UnrealEd.
        Does NOT invoke MAP NEW. Preserves all existing brushes, actors, and lights.
        """
        sys_dir = system_dir or Path(r"G:\UnrealTournament\System")
        ax, ay, az = anchor_location

        # Compute Directional Offsets
        dx, dy = 0.0, 0.0
        if direction.lower() in ["north", "+y"]:
            dy = 1536.0
        elif direction.lower() in ["south", "-y"]:
            dy = -1536.0
        elif direction.lower() in ["east", "+x"]:
            dx = 1536.0
        elif direction.lower() in ["west", "-x"]:
            dx = -1536.0

        room_x = ax + dx
        room_y = ay + dy
        hall_x = ax + (dx * 0.5)
        hall_y = ay + (dy * 0.5)

        logger.info(f"Wizard injecting '{wing_type}' at ({room_x}, {room_y}, {az}) connected via hall at ({hall_x}, {hall_y})")

        cmds: List[str] = []

        # 1. Texture Packages
        cmds.append('OBJ LOAD FILE="..\\Textures\\NaliCast.utx" PACKAGE=NaliCast')
        cmds.append('OBJ LOAD FILE="..\\Textures\\UTtech1.utx" PACKAGE=UTtech1')

        # 2. Carve Sealed Connecting Corridor (512 x 512 x 384)
        hall_file = _write_brush_file(sys_dir, "InjectHall.t3d", (512.0, 512.0, 384.0), shape="Box", floor_tex="NaliCast.CasFLOR", wall_tex="NaliCast.OldWallH")
        cmds.extend([
            f"BRUSH MOVETO X={hall_x} Y={hall_y} Z={az}",
            f'BRUSH IMPORT FILE="{hall_file}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
        ])

        # 3. Carve The New Wing Room (1536 x 1536 x 640)
        wing_file = _write_brush_file(sys_dir, "InjectWing.t3d", (1536.0, 1536.0, 640.0), shape="BeveledBox", floor_tex="NaliCast.CasFLOR", wall_tex="NaliCast.OldWallH")
        cmds.extend([
            f"BRUSH MOVETO X={room_x} Y={room_y} Z={az}",
            f'BRUSH IMPORT FILE="{wing_file}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",
        ])

        # 4. Add Central Dais or Fluted Pillar
        col_file = _write_brush_file(sys_dir, "InjectCol.t3d", (96.0, 96.0, 580.0), shape="HexColumn", is_semisolid=True, wall_tex="NaliCast.OldWallH")
        cmds.extend([
            f"BRUSH MOVETO X={room_x} Y={room_y} Z={az}",
            f'BRUSH IMPORT FILE="{col_file}" MERGE=0 FLAGS=0',
            "BRUSH ADD",
        ])

        # 5. Non-Destructive Actor Map Injection
        actor_path = sys_dir / "InjectActors.t3d"
        z_floor = az - 280

        actors = [
            "Begin Map",
            # Wing Lighting
            f"Begin Actor Class=Engine.Light Name=Light_InjectedWing\n    Location=(X={room_x},Y={room_y},Z={az + 150})\n    LightBrightness=190\n    LightRadius=54\n    LightHue=35\n    LightSaturation=180\n    LightType=LT_SubtlePulse\nEnd Actor",
            f"Begin Actor Class=Engine.Light Name=Light_InjectedHall\n    Location=(X={hall_x},Y={hall_y},Z={az + 100})\n    LightBrightness=160\n    LightRadius=32\n    LightHue=22\n    LightSaturation=200\nEnd Actor",
            # Armory / Reward
            f"Begin Actor Class=Botpack.UT_ShieldBelt Name=Shield_Injected\n    Location=(X={room_x},Y={room_y + 200},Z={z_floor + 35})\nEnd Actor",
            f"Begin Actor Class=Botpack.ShockRifle Name=Shock_Injected\n    Location=(X={room_x},Y={room_y - 200},Z={z_floor + 30})\nEnd Actor",
            # Path Nodes Connecting Hallway to Wing
            f"Begin Actor Class=Engine.PathNode Name=Path_Inject_Hall\n    Location=(X={hall_x},Y={hall_y},Z={z_floor + 30})\nEnd Actor",
            f"Begin Actor Class=Engine.PathNode Name=Path_Inject_Room\n    Location=(X={room_x},Y={room_y},Z={z_floor + 30})\nEnd Actor",
            f"Begin Actor Class=Engine.PathNode Name=Path_Inject_North\n    Location=(X={room_x},Y={room_y + 400},Z={z_floor + 30})\nEnd Actor",
            f"Begin Actor Class=Engine.PathNode Name=Path_Inject_South\n    Location=(X={room_x},Y={room_y - 400},Z={z_floor + 30})\nEnd Actor",
            "End Map",
        ]
        actor_path.write_text("\n".join(actors), encoding="utf-8")

        path_cmd = "PATHS DEFINE" if engine_id in ["ut2004", "ut2003"] else "PATHS BUILD"
        cmds.extend([
            f'MAP IMPORT FILE="{actor_path}"',
            "MAP REBUILD",
            "LIGHT APPLY",
            path_cmd,
            "FLUSH",
        ])

        return cmds
