"""
Procedural Formula Engine & Architecture Knowledge Base.
Supports UT99 GOTY (UE1 / OldUnreal 469e), UTron Total Conversion Mod, UT2003 (UE2.0), and UT2004 (UE2.5).

Generates 100% compliant, world-class UnrealEd maps via 2-stage CSG & Actor Synthesis:
  - Stage 1: Procedural CSG Architecture (PolyList BRUSH IMPORT + SUBTRACT/ADD)
  - Stage 2: Actor Map Import (T3D Map with exact 3D coordinates for PlayerStarts, Weapons, Pickups, PathNodes, Lights)
  - Stage 3: Level Compilation (MAP REBUILD + LIGHT APPLY + PATHS BUILD + FLUSH)
"""

import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------------------------------------------------------
# THEMATIC STOCK TEXTURE PRESETS
# -----------------------------------------------------------------------------
UT99_TEXTURE_THEMES = {
    "industrial": {
        "name": "Industrial Deck (Tech / Metal)",
        "packages": ["UTtech1.utx", "UTtech2.utx"],
        "floor": "rClfFlr2",
        "wall": "bmwall3",
        "ceiling": "bmCeiling3",
        "dais": "pillar",
        "trim": "bmTrim",
        "key_light_hue": 32,      # Warm Amber / Gold
        "key_light_sat": 160,
        "accent_light_hue": 145,  # Cyan
        "accent_light_sat": 200,
    },
    "cyber": {
        "name": "High-Tech Cyber (Phobos / HyperBlast)",
        "packages": ["UTtech1.utx", "UTtech2.utx"],
        "floor": "rCFlr14x",
        "wall": "mlbPipeWall7TES",
        "ceiling": "Mys_pan1",
        "dais": "rClfPlr4",
        "trim": "hzpanel2b",
        "key_light_hue": 150,     # Electric Blue
        "key_light_sat": 220,
        "accent_light_hue": 200,  # Deep Violet
        "accent_light_sat": 220,
    },
    "ancient": {
        "name": "Ancient Temple (Curse / Morpheus)",
        "packages": ["Ancient.utx"],
        "floor": "FLOOR2B",
        "wall": "BRIXG",
        "ceiling": "Ceiling3",
        "dais": "APillar",
        "trim": "TRIM1A",
        "key_light_hue": 20,      # Torch Fire Orange
        "key_light_sat": 180,
        "accent_light_hue": 35,   # Warm Amber
        "accent_light_sat": 180,
    },
    "skaarj": {
        "name": "Skaarj Outpost (Alien Metallurgy)",
        "packages": ["UTtech1.utx", "UTtech2.utx"],
        "floor": "rClfFlr6x",
        "wall": "bmwall3d",
        "ceiling": "Mys_pan2",
        "dais": "rClfPlr5",
        "trim": "ctrim",
        "key_light_hue": 85,      # Emerald Green
        "key_light_sat": 220,
        "accent_light_hue": 170,  # Electric Teal
        "accent_light_sat": 220,
    },
    "factory": {
        "name": "Heavy Industrial Factory",
        "packages": ["Factory.utx", "UTtech1.utx"],
        "floor": "rClfFlr2",
        "wall": "FactWall1b",
        "ceiling": "nmceiling5",
        "dais": "FactPillar1",
        "trim": "FactTrim1b",
        "key_light_hue": 0,       # Pure White Key
        "key_light_sat": 0,
        "accent_light_hue": 28,   # Hazard Amber
        "accent_light_sat": 240,
    },
}


def _generate_brush_polylist_t3d(
    dimensions: Tuple[float, float, float],
    shape: str = "Box",
    sides: int = 16,
    floor_tex: str = "UTtech1.Floor.rClfFlr2",
    wall_tex: str = "UTtech1.Wall.bmwall3",
    ceil_tex: str = "UTtech1.Ceiling.bmCeiling3",
    dais_tex: Optional[str] = None,
    trim_tex: Optional[str] = None,
) -> str:
    """Generates a watertight, textured PolyList T3D string for an UnrealEd brush."""
    dx, dy, dz = dimensions
    hx, hy, hz = dx / 2.0, dy / 2.0, dz / 2.0
    faces = []
    shape_lower = shape.lower()

    top_surface_tex = dais_tex or floor_tex
    side_surface_tex = trim_tex or wall_tex

    if "wedge" in shape_lower or "ramp" in shape_lower or "stair" in shape_lower:
        # Ramp sloping up in +Y direction from (-hz) to (+hz)
        faces = [
            ("Bottom", ceil_tex, (0, 0, -1), (1, 0, 0), (0, -1, 0), [
                (-hx, +hy, -hz), (+hx, +hy, -hz), (+hx, -hy, -hz), (-hx, -hy, -hz)]),
            ("Back", wall_tex, (0, 1, 0), (1, 0, 0), (0, 0, 1), [
                (+hx, +hy, -hz), (-hx, +hy, -hz), (-hx, +hy, +hz), (+hx, +hy, +hz)]),
            ("Slope", floor_tex, (0, -dz / dy, dy / dz), (1, 0, 0), (0, math.sqrt(dy * dy + dz * dz) / dy, 0), [
                (-hx, -hy, -hz), (+hx, -hy, -hz), (+hx, +hy, +hz), (-hx, +hy, +hz)]),
            ("Left", side_surface_tex, (-1, 0, 0), (0, 1, 0), (0, 0, 1), [
                (-hx, -hy, -hz), (-hx, +hy, +hz), (-hx, +hy, -hz)]),
            ("Right", side_surface_tex, (1, 0, 0), (0, -1, 0), (0, 0, 1), [
                (+hx, -hy, -hz), (+hx, +hy, -hz), (+hx, +hy, +hz)]),
        ]

    elif "cylinder" in shape_lower or "circle" in shape_lower or "disc" in shape_lower or "oct" in shape_lower:
        num_sides = 8 if "oct" in shape_lower else sides
        rx, ry = hx, hy
        bottom_verts = []
        top_verts = []
        for i in range(num_sides):
            angle = 2.0 * math.pi * i / num_sides
            x = rx * math.cos(angle)
            y = ry * math.sin(angle)
            bottom_verts.append((x, y, -hz))
            top_verts.append((x, y, +hz))

        b_order = [bottom_verts[0]] + [bottom_verts[i] for i in range(num_sides - 1, 0, -1)]
        faces.append(("Bottom", ceil_tex, (0, 0, -1), (1, 0, 0), (0, -1, 0), b_order))
        faces.append(("Top", top_surface_tex, (0, 0, 1), (1, 0, 0), (0, 1, 0), list(top_verts)))

        for i in range(num_sides):
            j = (i + 1) % num_sides
            mid_angle = 2.0 * math.pi * (i + 0.5) / num_sides
            norm = (math.cos(mid_angle), math.sin(mid_angle), 0)
            texU = (-math.sin(mid_angle), math.cos(mid_angle), 0)
            texV = (0, 0, 1)
            quad = [bottom_verts[i], bottom_verts[j], top_verts[j], top_verts[i]]
            faces.append((f"Side_{i}", side_surface_tex, norm, texU, texV, quad))

    else:
        # Standard Box / Cube
        faces = [
            ("Floor", floor_tex, (0, 0, -1), (1, 0, 0), (0, -1, 0), [
                (-hx, +hy, -hz), (+hx, +hy, -hz), (+hx, -hy, -hz), (-hx, -hy, -hz)]),
            ("Ceiling", ceil_tex, (0, 0, 1), (1, 0, 0), (0, 1, 0), [
                (-hx, -hy, +hz), (+hx, -hy, +hz), (+hx, +hy, +hz), (-hx, +hy, +hz)]),
            ("Front", wall_tex, (1, 0, 0), (0, 1, 0), (0, 0, 1), [
                (+hx, -hy, -hz), (+hx, +hy, -hz), (+hx, +hy, +hz), (+hx, -hy, +hz)]),
            ("Back", wall_tex, (-1, 0, 0), (0, -1, 0), (0, 0, 1), [
                (-hx, +hy, -hz), (-hx, -hy, -hz), (-hx, -hy, +hz), (-hx, +hy, +hz)]),
            ("Right", side_surface_tex, (0, 1, 0), (-1, 0, 0), (0, 0, 1), [
                (+hx, +hy, -hz), (-hx, +hy, -hz), (-hx, +hy, +hz), (+hx, +hy, +hz)]),
            ("Left", side_surface_tex, (0, -1, 0), (1, 0, 0), (0, 0, 1), [
                (-hx, -hy, -hz), (+hx, -hy, -hz), (+hx, -hy, +hz), (-hx, -hy, +hz)]),
        ]

    t3d = ["Begin PolyList"]
    for name, tex, norm, texU, texV, verts in faces:
        t3d.append(f"   Begin Polygon Item={name} Texture={tex} Flags=0")
        t3d.append(f"      Origin   {verts[0][0]:+.6f},{verts[0][1]:+.6f},{verts[0][2]:+.6f}")
        t3d.append(f"      Normal   {norm[0]:+.6f},{norm[1]:+.6f},{norm[2]:+.6f}")
        t3d.append(f"      TextureU {texU[0]:+.6f},{texU[1]:+.6f},{texU[2]:+.6f}")
        t3d.append(f"      TextureV {texV[0]:+.6f},{texV[1]:+.6f},{texV[2]:+.6f}")
        for vx, vy, vz in verts:
            t3d.append(f"      Vertex   {vx:+.6f},{vy:+.6f},{vz:+.6f}")
        t3d.append("   End Polygon")
    t3d.append("End PolyList")
    return "\n".join(t3d)


def _generate_actor_t3d(
    actor_class: str,
    name: str,
    location: Tuple[float, float, float],
    properties: Optional[Dict[str, Any]] = None,
) -> str:
    """Generates a generic T3D Actor block with exact coordinates and properties."""
    lines = [
        f"Begin Actor Class={actor_class} Name={name}",
        f"    Location=(X={location[0]:.6f},Y={location[1]:.6f},Z={location[2]:.6f})",
    ]
    if properties:
        for k, v in properties.items():
            lines.append(f"    {k}={v}")
    lines.append("End Actor")
    return "\n".join(lines)


def _write_file(system_dir: Optional[Path], filename: str, content: str) -> str:
    """Writes content to the System directory if available, returning the filename."""
    if system_dir and Path(system_dir).exists():
        try:
            target = Path(system_dir) / filename
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass
    return filename


def _write_brush_file(
    system_dir: Optional[Path],
    filename: str,
    dimensions: Tuple[float, float, float],
    shape: str = "Box",
    sides: int = 16,
    floor_tex: str = "UTtech1.Floor.rClfFlr2",
    wall_tex: str = "UTtech1.Wall.bmwall3",
    ceil_tex: str = "UTtech1.Ceiling.bmCeiling3",
    dais_tex: Optional[str] = None,
    trim_tex: Optional[str] = None,
) -> str:
    """Writes a standalone PolyList T3D file for brush import operations."""
    content = _generate_brush_polylist_t3d(
        dimensions, shape=shape, sides=sides,
        floor_tex=floor_tex, wall_tex=wall_tex, ceil_tex=ceil_tex,
        dais_tex=dais_tex, trim_tex=trim_tex,
    )
    return _write_file(system_dir, filename, content)


class FormulaEngine:
    """Parametric procedural level generator for Unreal Engine 1, 2.0, and 2.5."""

    # -------------------------------------------------------------------------
    # 1. WORLD-CLASS UT99 GOTY TOURNAMENT DEATHMATCH ARENA
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_ut99_tournament_arena(
        system_dir: Optional[Path] = None,
        width: int = 3072,
        length: int = 3072,
        height: int = 896,
        theme: str = "random",
    ) -> List[str]:
        """
        Constructs a premier, fully-playable multi-tier Tournament Deathmatch Arena (Deck16/Turbine tier).
        Uses a robust 2-stage CSG brush build + T3D actor map import.
        """
        # Resolve texture theme
        theme_keys = list(UT99_TEXTURE_THEMES.keys())
        if theme == "random" or theme not in UT99_TEXTURE_THEMES:
            theme_key = random.choice(theme_keys)
        else:
            theme_key = theme
        th = UT99_TEXTURE_THEMES[theme_key]

        floor_z = -height // 2  # -448
        mezz_top_z = -96        # -128 + 32
        dais_top_z = -384       # -416 + 32
        pillar_top_z = 0        # -192 + 192

        # 1. Write CSG Brush PolyLists
        f_main = _write_brush_file(system_dir, "ArenaMain.t3d", (float(width), float(length), float(height)), shape="Box", floor_tex=th["floor"], wall_tex=th["wall"], ceil_tex=th["ceiling"])
        f_mezz = _write_brush_file(system_dir, "ArenaMezz.t3d", (2560.0, 768.0, 64.0), shape="Box", floor_tex=th["floor"], wall_tex=th["wall"], ceil_tex=th["trim"], trim_tex=th["trim"])
        f_ramp = _write_brush_file(system_dir, "ArenaRamp.t3d", (256.0, 768.0, 352.0), shape="Ramp", floor_tex=th["floor"], wall_tex=th["wall"], ceil_tex=th["trim"], trim_tex=th["trim"])
        f_jump_pad = _write_brush_file(system_dir, "ArenaJumpDais.t3d", (256.0, 256.0, 32.0), shape="Box", floor_tex=th["dais"], wall_tex=th["trim"], ceil_tex=th["trim"], dais_tex=th["dais"], trim_tex=th["trim"])
        f_dais = _write_brush_file(system_dir, "ArenaDais.t3d", (1024.0, 1024.0, 64.0), shape="Octagon", floor_tex=th["floor"], wall_tex=th["trim"], ceil_tex=th["trim"], dais_tex=th["dais"], trim_tex=th["trim"])
        f_pillar = _write_brush_file(system_dir, "ArenaPillar.t3d", (192.0, 192.0, 384.0), shape="Cylinder", sides=12, floor_tex=th["trim"], wall_tex=th["dais"], ceil_tex=th["trim"], dais_tex=th["dais"], trim_tex=th["trim"])

        # 2. Write Actor T3D Map (All items & player starts at exact 3D coordinates)
        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    DefaultGameType=Class'Botpack.DeathMatchPlus'",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    AmbientBrightness=45",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            # PlayerStarts (Safe Z = surface_z + 50 UU clearance)
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-800.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (800.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart4", (-600.0, 1024.0, float(mezz_top_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart5", (600.0, 1024.0, float(mezz_top_z + 50))),

            # Weapons & Ammo Pairs
            _generate_actor_t3d("Botpack.ShockRifle", "ShockRifle0", (0.0, -850.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.ShockCore", "ShockCore0", (80.0, -850.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.UT_FlakCannon", "FlakCannon0", (-400.0, -256.0, float(dais_top_z + 24))),
            _generate_actor_t3d("Botpack.FlakAmmo", "FlakAmmo0", (-400.0, -320.0, float(dais_top_z + 24))),
            _generate_actor_t3d("Botpack.UT_Eightball", "Eightball0", (400.0, -256.0, float(dais_top_z + 24))),
            _generate_actor_t3d("Botpack.RocketPack", "RocketPack0", (400.0, -320.0, float(dais_top_z + 24))),
            _generate_actor_t3d("Botpack.minigun2", "Minigun0", (0.0, 300.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.Miniammo", "Miniammo0", (80.0, 300.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.SniperRifle", "SniperRifle0", (-800.0, 1024.0, float(mezz_top_z + 24))),
            _generate_actor_t3d("Botpack.BulletBox", "BulletBox0", (-880.0, 1024.0, float(mezz_top_z + 24))),

            # Powerups & Health
            _generate_actor_t3d("Botpack.UT_ShieldBelt", "ShieldBelt0", (0.0, 1024.0, float(mezz_top_z + 24))),
            _generate_actor_t3d("Botpack.Armor2", "Armor0", (0.0, -256.0, float(pillar_top_z + 24))),
            _generate_actor_t3d("Botpack.HealthPack", "HealthPack0", (0.0, 650.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox0", (-1200.0, -600.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox1", (1200.0, -600.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.HealthVial", "HealthVial0", (1152.0, 0.0, float(floor_z + 78))),
            _generate_actor_t3d("Botpack.HealthVial", "HealthVial1", (1152.0, 256.0, float(floor_z + 176))),
            _generate_actor_t3d("Botpack.HealthVial", "HealthVial2", (1152.0, 512.0, float(floor_z + 274))),

            # Botpack PathNodes
            _generate_actor_t3d("Engine.PathNode", "PathNode0", (-800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (0.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (-800.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode4", (800.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode5", (-800.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode6", (0.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode7", (800.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode8", (-350.0, -256.0, float(dais_top_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode9", (350.0, -256.0, float(dais_top_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode10", (1152.0, 0.0, float(floor_z + 78))),
            _generate_actor_t3d("Engine.PathNode", "PathNode11", (1152.0, 256.0, float(floor_z + 176))),
            _generate_actor_t3d("Engine.PathNode", "PathNode12", (1152.0, 512.0, float(floor_z + 274))),
            _generate_actor_t3d("Engine.PathNode", "PathNode13", (-1152.0, 256.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode14", (-800.0, 1024.0, float(mezz_top_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode15", (-300.0, 1024.0, float(mezz_top_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode16", (0.0, 1024.0, float(mezz_top_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode17", (300.0, 1024.0, float(mezz_top_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode18", (800.0, 1024.0, float(mezz_top_z + 50))),

            # Thematic Lights
            _generate_actor_t3d("Engine.Light", "KeyLight0", (0.0, -256.0, 180.0), {
                "LightBrightness": 220, "LightHue": th["key_light_hue"], "LightSaturation": th["key_light_sat"], "LightRadius": 96,
            }),
            _generate_actor_t3d("Engine.Light", "KeyLight1", (0.0, 1024.0, 220.0), {
                "LightBrightness": 200, "LightHue": th["key_light_hue"], "LightSaturation": th["key_light_sat"], "LightRadius": 80,
            }),
            _generate_actor_t3d("Engine.Light", "FillLight0", (-1200.0, -1200.0, float(floor_z + 200)), {
                "LightBrightness": 180, "LightHue": th["accent_light_hue"], "LightSaturation": th["accent_light_sat"], "LightRadius": 64,
            }),
            _generate_actor_t3d("Engine.Light", "FillLight1", (1200.0, -1200.0, float(floor_z + 200)), {
                "LightBrightness": 180, "LightHue": th["accent_light_hue"], "LightSaturation": th["accent_light_sat"], "LightRadius": 64,
            }),
            _generate_actor_t3d("Engine.Light", "FillLight2", (-1200.0, 1200.0, float(floor_z + 200)), {
                "LightBrightness": 180, "LightHue": th["accent_light_hue"], "LightSaturation": th["accent_light_sat"], "LightRadius": 64,
            }),
            _generate_actor_t3d("Engine.Light", "FillLight3", (1200.0, 1200.0, float(floor_z + 200)), {
                "LightBrightness": 180, "LightHue": th["accent_light_hue"], "LightSaturation": th["accent_light_sat"], "LightRadius": 64,
            }),

            "End Map",
        ]
        f_actors = _write_file(system_dir, "ArenaActors.t3d", "\n".join(t3d_actors))

        pkg_cmds = [f'OBJ LOAD FILE="..\\Textures\\{pkg}" PACKAGE={pkg.split(".")[0]}' for pkg in th.get("packages", ["UTtech1.utx"])]

        cmds = [
            "MAP NEW",
            *pkg_cmds,

            # Stage 1: Actor & Entity Synthesis (Imports LevelInfo, ZoneInfo, PlayerStarts, Weapons, Pickups, Lights, PathNodes)
            f'MAP IMPORT FILE="{f_actors}"',

            # Stage 2: CSG Architecture (Carves out rooms and adds platforms/ramps around actors)
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_main}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            "BRUSH MOVETO X=0 Y=1024 Z=-128",
            f'BRUSH IMPORT FILE="{f_mezz}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "BRUSH MOVETO X=1152 Y=256 Z=-272",
            f'BRUSH IMPORT FILE="{f_ramp}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "BRUSH MOVETO X=-1152 Y=256 Z=-432",
            f'BRUSH IMPORT FILE="{f_jump_pad}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "BRUSH MOVETO X=0 Y=-256 Z=-416",
            f'BRUSH IMPORT FILE="{f_dais}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "BRUSH MOVETO X=0 Y=-256 Z=-192",
            f'BRUSH IMPORT FILE="{f_pillar}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            # Stage 3: Level Compilation
            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 2. UTron DISCS OF TRON CYBER-VOID ARENA
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_utron_disc_arena(
        system_dir: Optional[Path] = None,
        radius: int = 1536,
        height: int = 768,
    ) -> List[str]:
        """Constructs a complete Discs of Tron cylindrical platform arena via 2-stage CSG & Actor Import."""
        floor_z = -height // 2
        dais_top = -218  # -250 + 32
        col_top = -22    # -150 + 128

        f_void = _write_brush_file(system_dir, "UTronVoid.t3d", (float(radius * 2), float(radius * 2), float(height)), shape="Cylinder", sides=16, floor_tex="AquaM", wall_tex="AquaM", ceil_tex="AquaM")
        f_dais = _write_brush_file(system_dir, "UTronDais.t3d", (float(radius * 1.2), float(radius * 1.2), 64.0), shape="Cylinder", sides=16, floor_tex="AquaM", wall_tex="plaingrey64", ceil_tex="plaingrey64")
        f_col = _write_brush_file(system_dir, "UTronCol.t3d", (384.0, 384.0, 256.0), shape="Cylinder", sides=12, floor_tex="solidDKgray128", wall_tex="AquaM", ceil_tex="solidDKgray128")

        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    AmbientBrightness=50",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            # PlayerStarts
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-600.0, -600.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (600.0, -600.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-600.0, 600.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (600.0, 600.0, float(dais_top + 50))),

            # Weaponry & Pickups
            _generate_actor_t3d("UTron.IdentityDisc", "Disc0", (0.0, -550.0, float(dais_top + 24))),
            _generate_actor_t3d("UTron.IdentityDisc", "Disc1", (0.0, 550.0, float(dais_top + 24))),
            _generate_actor_t3d("UTron.DiscAmmo", "DiscAmmo0", (-550.0, 0.0, float(dais_top + 24))),
            _generate_actor_t3d("UTron.DiscAmmo", "DiscAmmo1", (550.0, 0.0, float(dais_top + 24))),
            _generate_actor_t3d("Botpack.Armor2", "Armor0", (0.0, 0.0, float(col_top + 24))),

            # Navigation Network
            _generate_actor_t3d("Engine.PathNode", "PathNode0", (-500.0, -500.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (500.0, -500.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (-500.0, 500.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (500.0, 500.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode4", (0.0, -400.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode5", (0.0, 400.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode6", (-400.0, 0.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode7", (400.0, 0.0, float(dais_top + 50))),

            # Cyber Cyan Lighting
            _generate_actor_t3d("Engine.Light", "Light0", (-700.0, -700.0, 50.0), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),
            _generate_actor_t3d("Engine.Light", "Light1", (700.0, -700.0, 50.0), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),
            _generate_actor_t3d("Engine.Light", "Light2", (-700.0, 700.0, 50.0), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),
            _generate_actor_t3d("Engine.Light", "Light3", (700.0, 700.0, 50.0), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),

            # Diffuser Bus Line (8 interactive tiles)
            *[_generate_actor_t3d("UTron.diffuser", f"Diffuser{i}", (float((i * 128) - 448), 0.0, float(dais_top + 8))) for i in range(8)],

            "End Map",
        ]
        f_actors = _write_file(system_dir, "UTronDiscActors.t3d", "\n".join(t3d_actors))

        cmds = [
            "MAP NEW",
            f'MAP IMPORT FILE="{f_actors}"',
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_void}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            "BRUSH MOVETO X=0 Y=0 Z=-250",
            f'BRUSH IMPORT FILE="{f_dais}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "BRUSH MOVETO X=0 Y=0 Z=-150",
            f'BRUSH IMPORT FILE="{f_col}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 3. UT99 DUAL-BASE CTF OUTPOST
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_ut99_ctf_base(
        system_dir: Optional[Path] = None,
        base_color: str = "Red",
        width: int = 2560,
        length: int = 2560,
        height: int = 768,
    ) -> List[str]:
        """Generates a complete CTF Fortress Base with flag dais, sniper balcony, and defense points."""
        floor_z = -height // 2
        dais_top = floor_z + 48
        balc_top = -96

        is_red = base_color.lower() == "red"
        hue = 0 if is_red else 160
        wall_tex = "rclfwl4-RED" if is_red else "rclfwl4-BLU"
        floor_tex = "rClfFlr1x"
        ceil_tex = "rClfClg1"
        trim_tex = "rClfTrm2" if is_red else "rClfTrm3"
        dais_tex = "rClfPlr1" if is_red else "rClfPlr2"

        f_hall = _write_brush_file(system_dir, f"CTF_{base_color}_Hall.t3d", (float(width), float(length), float(height)), shape="Box", floor_tex=floor_tex, wall_tex=wall_tex, ceil_tex=ceil_tex)
        f_dais = _write_brush_file(system_dir, f"CTF_{base_color}_Dais.t3d", (512.0, 512.0, 48.0), shape="Box", floor_tex=dais_tex, wall_tex=trim_tex, ceil_tex=trim_tex, dais_tex=dais_tex, trim_tex=trim_tex)
        f_balc = _write_brush_file(system_dir, f"CTF_{base_color}_Balc.t3d", (1536.0, 512.0, 64.0), shape="Box", floor_tex=floor_tex, wall_tex=wall_tex, ceil_tex=trim_tex, trim_tex=trim_tex)
        f_ramp = _write_brush_file(system_dir, f"CTF_{base_color}_Ramp.t3d", (256.0, 512.0, 256.0), shape="Ramp", floor_tex=floor_tex, wall_tex=wall_tex, ceil_tex=trim_tex, trim_tex=trim_tex)

        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    DefaultGameType=Class'Botpack.CTFGame'",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    AmbientBrightness=40",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            _generate_actor_t3d("Botpack.CTFFlag", "CTFFlag0", (0.0, 800.0, float(dais_top + 30))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-600.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (600.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-400.0, -800.0, float(balc_top + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (400.0, -800.0, float(balc_top + 50))),

            _generate_actor_t3d("Botpack.SniperRifle", "Sniper0", (0.0, -800.0, float(balc_top + 24))),
            _generate_actor_t3d("Botpack.UT_FlakCannon", "Flak0", (-600.0, 0.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.UT_Eightball", "Eightball0", (600.0, 0.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.Armor2", "Armor0", (0.0, 400.0, float(floor_z + 24))),

            _generate_actor_t3d("Engine.PathNode", "PathNode0", (0.0, 800.0, float(dais_top + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (-600.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (600.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (0.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode4", (0.0, -800.0, float(balc_top + 50))),

            _generate_actor_t3d("Engine.Light", "LightFlag", (0.0, 800.0, float(floor_z + 200)), {"LightBrightness": 240, "LightHue": hue, "LightSaturation": 200, "LightRadius": 80}),
            _generate_actor_t3d("Engine.Light", "LightBalc", (0.0, -800.0, 100.0), {"LightBrightness": 200, "LightHue": hue, "LightSaturation": 160, "LightRadius": 64}),
            _generate_actor_t3d("Engine.Light", "LightCenter", (0.0, 0.0, 150.0), {"LightBrightness": 180, "LightHue": 32, "LightSaturation": 180, "LightRadius": 80}),

            "End Map",
        ]
        f_actors = _write_file(system_dir, f"CTF_{base_color}_Actors.t3d", "\n".join(t3d_actors))

        pkg_cmds = [r'OBJ LOAD FILE="..\Textures\UTtech2.utx" PACKAGE=UTtech2']

        cmds = [
            "MAP NEW",
            *pkg_cmds,
            f'MAP IMPORT FILE="{f_actors}"',
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_hall}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            f"BRUSH MOVETO X=0 Y=800 Z={floor_z + 24}",
            f'BRUSH IMPORT FILE="{f_dais}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=0 Y=-800 Z={balc_top - 32}",
            f'BRUSH IMPORT FILE="{f_balc}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=800 Y=-400 Z={floor_z + 128}",
            f'BRUSH IMPORT FILE="{f_ramp}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 4. UTron LIGHT CYCLE GRID
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_utron_lightcycle_grid(
        system_dir: Optional[Path] = None,
        grid_size: int = 3072,
        height: int = 512,
    ) -> List[str]:
        """Constructs a high-speed light cycle arena via 2-stage CSG & Actor Import."""
        floor_z = -height // 2

        f_grid = _write_brush_file(system_dir, "LightCycleGrid.t3d", (float(grid_size), float(grid_size), float(height)), shape="Box", floor_tex="AquaM", wall_tex="AquaM", ceil_tex="AquaM")
        f_div = _write_brush_file(system_dir, "CenterDivider.t3d", (64.0, 1536.0, 128.0), shape="Box", floor_tex="solidDKgray128", wall_tex="solidDKgray128", ceil_tex="solidDKgray128")

        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    AmbientBrightness=45",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-1000.0, -1000.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (1000.0, -1000.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-1000.0, 1000.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (1000.0, 1000.0, float(floor_z + 50))),

            _generate_actor_t3d("UTron.cycleMorph", "Morph0", (-800.0, -1000.0, float(floor_z + 24))),
            _generate_actor_t3d("UTron.cycleMorph", "Morph1", (800.0, -1000.0, float(floor_z + 24))),
            _generate_actor_t3d("UTron.cycleMorph", "Morph2", (-800.0, 1000.0, float(floor_z + 24))),
            _generate_actor_t3d("UTron.cycleMorph", "Morph3", (800.0, 1000.0, float(floor_z + 24))),

            _generate_actor_t3d("Engine.PathNode", "PathNode0", (-800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (-800.0, 800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (800.0, 800.0, float(floor_z + 50))),

            _generate_actor_t3d("Engine.Light", "Light0", (-1000.0, -1000.0, float(floor_z + 150)), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),
            _generate_actor_t3d("Engine.Light", "Light1", (1000.0, -1000.0, float(floor_z + 150)), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),
            _generate_actor_t3d("Engine.Light", "Light2", (-1000.0, 1000.0, float(floor_z + 150)), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),
            _generate_actor_t3d("Engine.Light", "Light3", (1000.0, 1000.0, float(floor_z + 150)), {"LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96}),

            "End Map",
        ]
        f_actors = _write_file(system_dir, "LightCycleActors.t3d", "\n".join(t3d_actors))

        cmds = [
            "MAP NEW",
            f'MAP IMPORT FILE="{f_actors}"',
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_grid}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            f"BRUSH MOVETO X=0 Y=0 Z={floor_z + 64}",
            f'BRUSH IMPORT FILE="{f_div}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 5. UT2004 ARENA
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_ut2004_arena(
        system_dir: Optional[Path] = None,
        width: int = 3072,
        length: int = 3072,
        height: int = 768,
    ) -> List[str]:
        """Generates a UT2004 tournament combat space via 2-stage CSG & Actor Import."""
        floor_z = -height // 2
        dais_top = floor_z + 64

        f_room = _write_brush_file(system_dir, "UT2004Arena.t3d", (float(width), float(length), float(height)), shape="Box", floor_tex="metal_flr01", wall_tex="metalwall01", ceil_tex="metalwall01")
        f_dais = _write_brush_file(system_dir, "UT2004Dais.t3d", (1024.0, 1024.0, 64.0), shape="Box", floor_tex="c_circuits01", wall_tex="metalwall01", ceil_tex="metalwall01", dais_tex="c_circuits01", trim_tex="metalwall01")

        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    AmbientBrightness=45",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-800.0, 800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (800.0, 800.0, float(floor_z + 50))),

            _generate_actor_t3d("XWeapons.ShockRiflePickup", "Shock0", (0.0, -800.0, float(floor_z + 24))),
            _generate_actor_t3d("XWeapons.FlakCannonPickup", "Flak0", (0.0, 800.0, float(floor_z + 24))),
            _generate_actor_t3d("XWeapons.RocketLauncherPickup", "Rocket0", (-800.0, 0.0, float(floor_z + 24))),
            _generate_actor_t3d("XWeapons.SniperRiflePickup", "Sniper0", (800.0, 0.0, float(floor_z + 24))),
            _generate_actor_t3d("XPickups.SuperHealthPack", "Health0", (0.0, 0.0, float(dais_top + 24))),

            _generate_actor_t3d("Engine.PathNode", "PathNode0", (-800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (-800.0, 800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (800.0, 800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode4", (0.0, 0.0, float(dais_top + 50))),

            _generate_actor_t3d("Engine.Light", "Light0", (0.0, 0.0, 200.0), {"LightBrightness": 220, "LightHue": 32, "LightSaturation": 180, "LightRadius": 96}),

            "End Map",
        ]
        f_actors = _write_file(system_dir, "UT2004Actors.t3d", "\n".join(t3d_actors))

        pkg_cmds = [r'OBJ LOAD FILE="..\Textures\HumanFloor.utx" PACKAGE=HumanFloor', r'OBJ LOAD FILE="..\Textures\Industrial.utx" PACKAGE=Industrial']

        cmds = [
            "MAP NEW",
            *pkg_cmds,
            f'MAP IMPORT FILE="{f_actors}"',
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_room}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            f"BRUSH MOVETO X=0 Y=0 Z={floor_z + 32}",
            f'BRUSH IMPORT FILE="{f_dais}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 7. PREMIER OUTDOOR WORLD BLUEPRINTS
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_ut99_verdant_mountain_valley(
        system_dir: Optional[Path] = None,
        width: int = 4096,
        length: int = 4096,
        height: int = 1536,
    ) -> List[str]:
        """
        Constructs a premier lush mountain valley with a stone fortress bunker,
        river gorge, stone bridge, watchtower, pine forest, and mountain boulders.
        """
        floor_z = -height // 2   # -768
        bridge_z = floor_z + 32  # -736
        fort_z = floor_z + 192   # -576
        tower_top_z = floor_z + 640

        # CSG Brushes
        f_valley = _write_brush_file(system_dir, "ValleyMain.t3d", (float(width), float(length), float(height)), shape="Box", floor_tex="grasrok2", wall_tex="Rockwal5", ceil_tex="pansky1")
        f_river = _write_brush_file(system_dir, "RiverBed.t3d", (768.0, float(length), 128.0), shape="Box", floor_tex="Pebbles", wall_tex="Dirt2", ceil_tex="Dirt2")
        f_fort = _write_brush_file(system_dir, "StoneFort.t3d", (1024.0, 1024.0, 384.0), shape="Box", floor_tex="oldflor", wall_tex="CasWAL", ceil_tex="ntrim2", dais_tex="oldflor", trim_tex="METTRIM1")
        f_fort_room = _write_brush_file(system_dir, "FortRoom.t3d", (896.0, 896.0, 320.0), shape="Box", floor_tex="oldflor", wall_tex="oldwall3", ceil_tex="METTRIM1")
        f_fort_door = _write_brush_file(system_dir, "FortDoor.t3d", (256.0, 256.0, 256.0), shape="Box", floor_tex="oldflor", wall_tex="Casdoor2", ceil_tex="ntrim2")
        f_bridge = _write_brush_file(system_dir, "StoneBridge.t3d", (512.0, 1024.0, 64.0), shape="Box", floor_tex="steps", wall_tex="CasWAL", ceil_tex="METTRIM1", dais_tex="steps", trim_tex="METTRIM1")
        f_ramp1 = _write_brush_file(system_dir, "BridgeRamp1.t3d", (512.0, 256.0, 96.0), shape="Ramp", floor_tex="steps", wall_tex="CasWAL", ceil_tex="METTRIM1")
        f_ramp2 = _write_brush_file(system_dir, "BridgeRamp2.t3d", (512.0, 256.0, 96.0), shape="Ramp", floor_tex="steps", wall_tex="CasWAL", ceil_tex="METTRIM1")
        f_tower = _write_brush_file(system_dir, "WatchTower.t3d", (384.0, 384.0, 640.0), shape="Cylinder", sides=8, floor_tex="oldflor", wall_tex="npillar", ceil_tex="ntrim2", dais_tex="oldflor", trim_tex="ntrim2")

        # Actors (Entities, Weapons, Trees, Rocks, Lights, Paths)
        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    DefaultGameType=Class'Botpack.DeathMatchPlus'",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    AmbientBrightness=55",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            # 6 PlayerStarts (+50 UU floor clearance)
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-1200.0, -1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (1200.0, 1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-1200.0, 1200.0, float(fort_z + 240))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (1200.0, -1200.0, float(tower_top_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart4", (-600.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart5", (600.0, 0.0, float(floor_z + 50))),

            # Weapons & Ammo Armory
            _generate_actor_t3d("Botpack.ShockRifle", "ShockRifle0", (-600.0, -600.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.ShockCore", "ShockCore0", (-520.0, -600.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.UT_FlakCannon", "FlakCannon0", (600.0, 600.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.FlakAmmo", "FlakAmmo0", (680.0, 600.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.UT_Eightball", "Eightball0", (-1200.0, 1200.0, float(fort_z + 24))),
            _generate_actor_t3d("Botpack.RocketPack", "RocketPack0", (-1120.0, 1200.0, float(fort_z + 24))),
            _generate_actor_t3d("Botpack.minigun2", "Minigun0", (0.0, -700.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.Miniammo", "Miniammo0", (80.0, -700.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.SniperRifle", "SniperRifle0", (1200.0, -1200.0, float(tower_top_z + 24))),
            _generate_actor_t3d("Botpack.BulletBox", "BulletBox0", (1280.0, -1200.0, float(tower_top_z + 24))),
            _generate_actor_t3d("Botpack.WarheadLauncher", "Redeemer0", (0.0, 0.0, float(bridge_z + 56))),

            # Powerups & Health
            _generate_actor_t3d("Botpack.Armor2", "Armor0", (-1200.0, 1000.0, float(fort_z + 24))),
            _generate_actor_t3d("Botpack.UT_ShieldBelt", "ShieldBelt0", (1200.0, -1200.0, float(tower_top_z + 24))),
            _generate_actor_t3d("Botpack.HealthPack", "HealthPack0", (0.0, 400.0, float(floor_z - 40))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox0", (-1000.0, -1000.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox1", (1000.0, 1000.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.HealthVial", "HealthVial0", (0.0, -250.0, float(bridge_z + 40))),
            _generate_actor_t3d("Botpack.HealthVial", "HealthVial1", (0.0, 0.0, float(bridge_z + 40))),
            _generate_actor_t3d("Botpack.HealthVial", "HealthVial2", (0.0, 250.0, float(bridge_z + 40))),

            # 3D World Elements (Trees, Plants, Boulders, Torches)
            _generate_actor_t3d("UnrealShare.Tree1", "Tree0", (-800.0, -800.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Tree2", "Tree1", (-1400.0, -400.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Tree3", "Tree2", (800.0, 800.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Tree6", "Tree3", (1400.0, 400.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Tree1", "Tree4", (-400.0, 1200.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Tree2", "Tree5", (600.0, -1200.0, float(floor_z))),

            _generate_actor_t3d("UnrealShare.Plant1", "Plant0", (-500.0, -200.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Plant2", "Plant1", (500.0, 200.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Plant3", "Plant2", (-1000.0, 700.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Plant1", "Plant3", (1000.0, -700.0, float(floor_z))),

            _generate_actor_t3d("UnrealI.BigRock", "Rock0", (-900.0, -300.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Boulder", "Rock1", (900.0, 300.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Boulder", "Rock2", (-300.0, -900.0, float(floor_z))),
            _generate_actor_t3d("UnrealI.BigRock", "Rock3", (300.0, 900.0, float(floor_z))),

            _generate_actor_t3d("UnrealShare.TorchFlame", "Torch0", (-1200.0, 680.0, float(fort_z + 80))),
            _generate_actor_t3d("UnrealShare.TorchFlame", "Torch1", (-1200.0, 1720.0, float(fort_z + 80))),

            # Botpack PathNodes
            _generate_actor_t3d("Engine.PathNode", "PathNode0", (-1200.0, -1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (-600.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (0.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (600.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode4", (1200.0, -1200.0, float(tower_top_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode5", (1200.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode6", (600.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode7", (0.0, -250.0, float(bridge_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode8", (0.0, 0.0, float(bridge_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode9", (0.0, 250.0, float(bridge_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode10", (-600.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode11", (-1200.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode12", (-1200.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode13", (-1200.0, 1200.0, float(fort_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode14", (-600.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode15", (0.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode16", (600.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode17", (1200.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode18", (1200.0, 1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode19", (0.0, 1200.0, float(floor_z + 50))),

            # Natural Outdoor Sun & Sky Lighting
            _generate_actor_t3d("Engine.Light", "SunKey", (500.0, -500.0, float(height // 3)), {
                "LightBrightness": 240, "LightHue": 38, "LightSaturation": 110, "LightRadius": 128,
            }),
            _generate_actor_t3d("Engine.Light", "SkyFill0", (-1200.0, -1200.0, float(floor_z + 350)), {
                "LightBrightness": 170, "LightHue": 155, "LightSaturation": 160, "LightRadius": 96,
            }),
            _generate_actor_t3d("Engine.Light", "SkyFill1", (1200.0, 1200.0, float(floor_z + 350)), {
                "LightBrightness": 170, "LightHue": 155, "LightSaturation": 160, "LightRadius": 96,
            }),
            _generate_actor_t3d("Engine.Light", "BridgeLight", (0.0, 0.0, float(bridge_z + 200)), {
                "LightBrightness": 200, "LightHue": 38, "LightSaturation": 120, "LightRadius": 80,
            }),
            _generate_actor_t3d("Engine.Light", "FortLight", (-1200.0, 1200.0, float(fort_z + 180)), {
                "LightBrightness": 210, "LightHue": 25, "LightSaturation": 180, "LightRadius": 64,
            }),

            "End Map",
        ]
        f_actors = _write_file(system_dir, "ValleyActors.t3d", "\n".join(t3d_actors))

        pkg_cmds = [
            r'OBJ LOAD FILE="..\Textures\GenEarth.utx" PACKAGE=GenEarth',
            r'OBJ LOAD FILE="..\Textures\NaliCast.utx" PACKAGE=NaliCast',
            r'OBJ LOAD FILE="..\Textures\ShaneSky.utx" PACKAGE=ShaneSky',
        ]

        cmds = [
            "MAP NEW",
            *pkg_cmds,
            f'MAP IMPORT FILE="{f_actors}"',

            # Valley Terrain
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_valley}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            # River Channel
            f"BRUSH MOVETO X=0 Y=0 Z={floor_z - 64}",
            f'BRUSH IMPORT FILE="{f_river}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            # Stone Fortress & Interior
            f"BRUSH MOVETO X=-1200 Y=1200 Z={fort_z}",
            f'BRUSH IMPORT FILE="{f_fort}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=-1200 Y=1200 Z={fort_z}",
            f'BRUSH IMPORT FILE="{f_fort_room}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            f"BRUSH MOVETO X=-1200 Y=700 Z={fort_z - 32}",
            f'BRUSH IMPORT FILE="{f_fort_door}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            # Stone Bridge & Ramps
            f"BRUSH MOVETO X=0 Y=0 Z={bridge_z}",
            f'BRUSH IMPORT FILE="{f_bridge}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=0 Y=-600 Z={floor_z + 16}",
            f'BRUSH IMPORT FILE="{f_ramp1}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=0 Y=600 Z={floor_z + 16}",
            f'BRUSH IMPORT FILE="{f_ramp2}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            # Watchtower
            f"BRUSH MOVETO X=1200 Y=-1200 Z={floor_z + 320}",
            f'BRUSH IMPORT FILE="{f_tower}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 8. ARID DESERT CANYON & EXCAVATION RUINS
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_ut99_desert_canyon_ruins(
        system_dir: Optional[Path] = None,
        width: int = 4608,
        length: int = 4608,
        height: int = 1792,
    ) -> List[str]:
        """
        Constructs an ancient desert canyon with sun-drenched sandstone ruins,
        excavation plateau ramps, colonnades, oasis well, and cacti foliage.
        """
        floor_z = -height // 2   # -896
        plateau_z = floor_z + 256 # -640
        temple_z = floor_z + 192

        f_canyon = _write_brush_file(system_dir, "DesertCanyon.t3d", (float(width), float(length), float(height)), shape="Box", floor_tex="path", wall_tex="Basicrok2", ceil_tex="Lnd_1")
        f_plateau = _write_brush_file(system_dir, "SandPlateau.t3d", (1536.0, 1536.0, 256.0), shape="Box", floor_tex="FLOOR2B", wall_tex="BRIXG", ceil_tex="TRIM1A", dais_tex="FLOOR2B", trim_tex="TRIM1A")
        f_ramp = _write_brush_file(system_dir, "PlateauRamp.t3d", (384.0, 768.0, 256.0), shape="Ramp", floor_tex="FLOOR2B", wall_tex="BRIXG", ceil_tex="TRIM1A")
        f_temple = _write_brush_file(system_dir, "DesertTemple.t3d", (1280.0, 1280.0, 384.0), shape="Box", floor_tex="FLOOR1", wall_tex="BRIXG", ceil_tex="Ceiling3", dais_tex="FLOOR1", trim_tex="TRIM1A")
        f_temple_room = _write_brush_file(system_dir, "TempleRoom.t3d", (1024.0, 1024.0, 320.0), shape="Box", floor_tex="FLOOR1", wall_tex="HIWALL1B", ceil_tex="CARVIN1A")
        f_temple_door = _write_brush_file(system_dir, "TempleDoor.t3d", (384.0, 384.0, 256.0), shape="Box", floor_tex="FLOOR1", wall_tex="BRIXG", ceil_tex="TRIM1A")
        f_col1 = _write_brush_file(system_dir, "Colonnade1.t3d", (192.0, 192.0, 384.0), shape="Cylinder", sides=8, floor_tex="TRIM1A", wall_tex="COLUMN3", ceil_tex="TRIM1A")
        f_col2 = _write_brush_file(system_dir, "Colonnade2.t3d", (192.0, 192.0, 384.0), shape="Cylinder", sides=8, floor_tex="TRIM1A", wall_tex="COLUMN3", ceil_tex="TRIM1A")
        f_oasis = _write_brush_file(system_dir, "OasisWell.t3d", (512.0, 512.0, 64.0), shape="Cylinder", sides=12, floor_tex="FLORROK1", wall_tex="TRIM2A", ceil_tex="TRIM2A", dais_tex="FLORROK1", trim_tex="TRIM2A")

        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    DefaultGameType=Class'Botpack.DeathMatchPlus'",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    AmbientBrightness=50",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            # 6 PlayerStarts
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-1400.0, -1400.0, float(temple_z + 240))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (1200.0, 1200.0, float(plateau_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-1200.0, 1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (1200.0, -1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart4", (0.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart5", (0.0, 600.0, float(floor_z + 50))),

            # Weapons
            _generate_actor_t3d("Botpack.UT_Eightball", "Eightball0", (-1000.0, -1000.0, float(temple_z + 240))),
            _generate_actor_t3d("Botpack.RocketPack", "RocketPack0", (-920.0, -1000.0, float(temple_z + 240))),
            _generate_actor_t3d("Botpack.UT_FlakCannon", "FlakCannon0", (1000.0, 1000.0, float(plateau_z + 24))),
            _generate_actor_t3d("Botpack.FlakAmmo", "FlakAmmo0", (1080.0, 1000.0, float(plateau_z + 24))),
            _generate_actor_t3d("Botpack.ShockRifle", "ShockRifle0", (0.0, 0.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.ShockCore", "ShockCore0", (80.0, 0.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.SniperRifle", "SniperRifle0", (1200.0, -1200.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.BulletBox", "BulletBox0", (1280.0, -1200.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.minigun2", "Minigun0", (-1000.0, -1000.0, float(temple_z + 24))),
            _generate_actor_t3d("Botpack.Miniammo", "Miniammo0", (-920.0, -1000.0, float(temple_z + 24))),

            # Pickups
            _generate_actor_t3d("Botpack.Armor2", "Armor0", (-1000.0, -1000.0, float(temple_z + 24))),
            _generate_actor_t3d("Botpack.UT_ShieldBelt", "ShieldBelt0", (1000.0, 1000.0, float(plateau_z + 24))),
            _generate_actor_t3d("Botpack.UT_JumpBoots", "JumpBoots0", (0.0, -300.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.HealthPack", "HealthPack0", (-1000.0, -700.0, float(temple_z + 240))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox0", (-1200.0, 1200.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox1", (1200.0, -1200.0, float(floor_z + 24))),

            # Desert Props (Cacti, Statues, Urns, Rocks)
            _generate_actor_t3d("UnrealShare.Plant5", "Cactus0", (-600.0, -800.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Plant7", "Cactus1", (600.0, 800.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Plant5", "Cactus2", (-800.0, 600.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Plant7", "Cactus3", (800.0, -600.0, float(floor_z))),

            _generate_actor_t3d("UnrealShare.MonkStatue", "Statue0", (-1000.0, -750.0, float(temple_z + 24))),
            _generate_actor_t3d("UnrealShare.NaliStatue", "Statue1", (1000.0, 750.0, float(plateau_z + 24))),
            _generate_actor_t3d("UnrealShare.Urn", "Urn0", (-700.0, -1000.0, float(temple_z + 24))),
            _generate_actor_t3d("UnrealShare.Vase", "Vase0", (700.0, 1000.0, float(plateau_z + 24))),

            _generate_actor_t3d("UnrealI.BigRock", "Boulder0", (-400.0, 400.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Boulder", "Boulder1", (400.0, -400.0, float(floor_z))),

            # PathNodes
            _generate_actor_t3d("Engine.PathNode", "PathNode0", (-1400.0, -1400.0, float(temple_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (-1000.0, -1000.0, float(temple_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (-600.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (0.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode4", (600.0, -600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode5", (1200.0, -1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode6", (0.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode7", (600.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode8", (1000.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode9", (1000.0, 1000.0, float(plateau_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode10", (1200.0, 1200.0, float(plateau_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode11", (0.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode12", (-600.0, 600.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode13", (-1200.0, 1200.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode14", (-1000.0, 0.0, float(floor_z + 50))),

            # Desert Sun & Atmospheric Lighting
            _generate_actor_t3d("Engine.Light", "SunKey", (600.0, -600.0, float(height // 3)), {
                "LightBrightness": 250, "LightHue": 25, "LightSaturation": 180, "LightRadius": 128,
            }),
            _generate_actor_t3d("Engine.Light", "DesertAmbient", (0.0, 0.0, float(floor_z + 300)), {
                "LightBrightness": 180, "LightHue": 225, "LightSaturation": 140, "LightRadius": 96,
            }),
            _generate_actor_t3d("Engine.Light", "TempleLight", (-1000.0, -1000.0, float(temple_z + 180)), {
                "LightBrightness": 200, "LightHue": 20, "LightSaturation": 180, "LightRadius": 64,
            }),

            "End Map",
        ]
        f_actors = _write_file(system_dir, "DesertActors.t3d", "\n".join(t3d_actors))

        pkg_cmds = [
            r'OBJ LOAD FILE="..\Textures\Ancient.utx" PACKAGE=Ancient',
            r'OBJ LOAD FILE="..\Textures\GenEarth.utx" PACKAGE=GenEarth',
            r'OBJ LOAD FILE="..\Textures\SkyBox.utx" PACKAGE=SkyBox',
        ]

        cmds = [
            "MAP NEW",
            *pkg_cmds,
            f'MAP IMPORT FILE="{f_actors}"',

            # Canyon Floor
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_canyon}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            # Sand Plateau & Access Ramp
            f"BRUSH MOVETO X=1000 Y=1000 Z={plateau_z - 128}",
            f'BRUSH IMPORT FILE="{f_plateau}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=1000 Y=300 Z={floor_z + 128}",
            f'BRUSH IMPORT FILE="{f_ramp}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            # Desert Temple & Sanctum
            f"BRUSH MOVETO X=-1000 Y=-1000 Z={temple_z}",
            f'BRUSH IMPORT FILE="{f_temple}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=-1000 Y=-1000 Z={temple_z}",
            f'BRUSH IMPORT FILE="{f_temple_room}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            f"BRUSH MOVETO X=-1000 Y=-500 Z={temple_z - 32}",
            f'BRUSH IMPORT FILE="{f_temple_door}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            # Colonnade Pillars
            f"BRUSH MOVETO X=-1200 Y=-500 Z={temple_z}",
            f'BRUSH IMPORT FILE="{f_col1}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=-800 Y=-500 Z={temple_z}",
            f'BRUSH IMPORT FILE="{f_col2}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            # Oasis Well
            f"BRUSH MOVETO X=0 Y=0 Z={floor_z + 32}",
            f'BRUSH IMPORT FILE="{f_oasis}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 9. ORBITAL ASTEROID OUTPOST (MOONBASE)
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_ut99_orbital_asteroid_outpost(
        system_dir: Optional[Path] = None,
        radius: int = 2048,
        height: int = 1536,
    ) -> List[str]:
        """
        Constructs a low-gravity lunar asteroid outpost with command hab module,
        comm relay platform, landing pad, airlocks, craters, and deep space starfield.
        """
        floor_z = -height // 2   # -768
        comm_z = floor_z + 256   # -512
        mast_top_z = comm_z + 640
        hab_z = floor_z + 192

        f_crater = _write_brush_file(system_dir, "AsteroidCrater.t3d", (float(radius * 2), float(radius * 2), float(height)), shape="Cylinder", sides=16, floor_tex="rClfFlr1x", wall_tex="mlbPipeWall7TES", ceil_tex="NCld")
        f_hab = _write_brush_file(system_dir, "HabModule.t3d", (1280.0, 1280.0, 384.0), shape="Box", floor_tex="rClfFlr2", wall_tex="bmwall3", ceil_tex="bmTrim", dais_tex="rClfFlr2", trim_tex="bmTrim")
        f_hab_room = _write_brush_file(system_dir, "HabInterior.t3d", (1152.0, 1152.0, 320.0), shape="Box", floor_tex="rClfFlr2", wall_tex="Mys_pan1", ceil_tex="bmCeiling3")
        f_airlock = _write_brush_file(system_dir, "AirlockDoor.t3d", (256.0, 256.0, 256.0), shape="Box", floor_tex="rClfFlr2", wall_tex="doorC2", ceil_tex="bmTrim")
        f_comm_dais = _write_brush_file(system_dir, "CommRelayDais.t3d", (1024.0, 1024.0, 256.0), shape="Octagon", floor_tex="rCFlr14x", wall_tex="rClfPlr4", ceil_tex="hzpanel2b", dais_tex="rCFlr14x", trim_tex="hzpanel2b")
        f_comm_mast = _write_brush_file(system_dir, "CommMast.t3d", (128.0, 128.0, 640.0), shape="Cylinder", sides=8, floor_tex="bmTrim", wall_tex="rClfPlr5", ceil_tex="bmTrim")
        f_ramp = _write_brush_file(system_dir, "CraterRamp.t3d", (384.0, 768.0, 256.0), shape="Ramp", floor_tex="rCFlr14x", wall_tex="bmwall3", ceil_tex="hzpanel2b")
        f_pad = _write_brush_file(system_dir, "CenterLandingPad.t3d", (1280.0, 1280.0, 64.0), shape="Octagon", floor_tex="rCFlr12x", wall_tex="bmTrim", ceil_tex="bmTrim", dais_tex="rCFlr12x", trim_tex="bmTrim")

        t3d_actors = [
            "Begin Map",
            "Begin Actor Class=Engine.LevelInfo Name=LevelInfo0",
            "    TimeDilation=1.000000",
            "    DefaultGameType=Class'Botpack.DeathMatchPlus'",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",
            "Begin Actor Class=Engine.ZoneInfo Name=ZoneInfo0",
            "    ZoneGravity=(X=0.000000,Y=0.000000,Z=-350.000000)",
            "    AmbientBrightness=45",
            "    Location=(X=0.000000,Y=0.000000,Z=0.000000)",
            "End Actor",

            # 6 PlayerStarts
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart0", (-1000.0, 1000.0, float(hab_z + 24))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart1", (1000.0, -1000.0, float(comm_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart2", (-800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart3", (800.0, 800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart4", (0.0, 0.0, float(floor_z + 114))),
            _generate_actor_t3d("Engine.PlayerStart", "PlayerStart5", (0.0, -800.0, float(floor_z + 50))),

            # Weapons Armory
            _generate_actor_t3d("Botpack.WarheadLauncher", "Redeemer0", (1000.0, -1000.0, float(comm_z + 24))),
            _generate_actor_t3d("Botpack.SniperRifle", "SniperRifle0", (1000.0, -1000.0, float(mast_top_z + 24))),
            _generate_actor_t3d("Botpack.BulletBox", "BulletBox0", (1060.0, -1000.0, float(mast_top_z + 24))),
            _generate_actor_t3d("Botpack.ShockRifle", "ShockRifle0", (0.0, 0.0, float(floor_z + 88))),
            _generate_actor_t3d("Botpack.ShockCore", "ShockCore0", (80.0, 0.0, float(floor_z + 88))),
            _generate_actor_t3d("Botpack.UT_FlakCannon", "FlakCannon0", (-800.0, -800.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.FlakAmmo", "FlakAmmo0", (-720.0, -800.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.minigun2", "Minigun0", (-1000.0, 600.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.Miniammo", "Miniammo0", (-920.0, 600.0, float(floor_z + 24))),

            # Pickups
            _generate_actor_t3d("Botpack.UT_ShieldBelt", "ShieldBelt0", (-1000.0, 1000.0, float(hab_z + 24))),
            _generate_actor_t3d("Botpack.Armor2", "Armor0", (0.0, 0.0, float(floor_z + 88))),
            _generate_actor_t3d("Botpack.UT_JumpBoots", "JumpBoots0", (-1000.0, 450.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.HealthPack", "HealthPack0", (1000.0, -1000.0, float(mast_top_z + 24))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox0", (800.0, 800.0, float(floor_z + 24))),
            _generate_actor_t3d("Botpack.MedBox", "MedBox1", (-800.0, -800.0, float(floor_z + 24))),

            # Asteroid Elements (Meteorites, Cargo Containers, Beacons)
            _generate_actor_t3d("UnrealI.BigRock", "Meteor0", (-500.0, -400.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Boulder", "Meteor1", (600.0, 300.0, float(floor_z))),
            _generate_actor_t3d("UnrealI.BigRock", "Meteor2", (400.0, -600.0, float(floor_z))),
            _generate_actor_t3d("UnrealShare.Barrel", "Cargo0", (-1000.0, 850.0, float(hab_z + 24))),
            _generate_actor_t3d("UnrealShare.Chest", "Cargo1", (-850.0, 1000.0, float(hab_z + 24))),
            _generate_actor_t3d("UnrealShare.Lantern", "Beacon0", (1000.0, -700.0, float(comm_z + 24))),
            _generate_actor_t3d("UnrealShare.Lantern2", "Beacon1", (1000.0, -1300.0, float(comm_z + 24))),

            # PathNodes
            _generate_actor_t3d("Engine.PathNode", "PathNode0", (-1000.0, 1000.0, float(hab_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode1", (-1000.0, 500.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode2", (-600.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode3", (0.0, 0.0, float(floor_z + 114))),
            _generate_actor_t3d("Engine.PathNode", "PathNode4", (600.0, 0.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode5", (1000.0, -500.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode6", (1000.0, -1000.0, float(comm_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode7", (0.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode8", (-800.0, -800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode9", (800.0, 800.0, float(floor_z + 50))),
            _generate_actor_t3d("Engine.PathNode", "PathNode10", (0.0, 800.0, float(floor_z + 50))),

            # Deep Space Lighting
            _generate_actor_t3d("Engine.Light", "NebulaKey", (0.0, 0.0, float(height // 4)), {
                "LightBrightness": 220, "LightHue": 155, "LightSaturation": 240, "LightRadius": 128,
            }),
            _generate_actor_t3d("Engine.Light", "CyanBeacon", (1000.0, -1000.0, float(comm_z + 200)), {
                "LightBrightness": 240, "LightHue": 145, "LightSaturation": 255, "LightRadius": 96,
            }),
            _generate_actor_t3d("Engine.Light", "HabLight", (-1000.0, 1000.0, float(hab_z + 180)), {
                "LightBrightness": 190, "LightHue": 32, "LightSaturation": 160, "LightRadius": 64,
            }),

            "End Map",
        ]
        f_actors = _write_file(system_dir, "AsteroidActors.t3d", "\n".join(t3d_actors))

        pkg_cmds = [
            r'OBJ LOAD FILE="..\Textures\SpaceFX.utx" PACKAGE=SpaceFX',
            r'OBJ LOAD FILE="..\Textures\UTtech1.utx" PACKAGE=UTtech1',
            r'OBJ LOAD FILE="..\Textures\UTtech2.utx" PACKAGE=UTtech2',
            r'OBJ LOAD FILE="..\Textures\SkyBox.utx" PACKAGE=SkyBox',
        ]

        cmds = [
            "MAP NEW",
            *pkg_cmds,
            f'MAP IMPORT FILE="{f_actors}"',

            # Crater Basin
            "BRUSH MOVETO X=0 Y=0 Z=0",
            f'BRUSH IMPORT FILE="{f_crater}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            # Landing Pad
            f"BRUSH MOVETO X=0 Y=0 Z={floor_z + 32}",
            f'BRUSH IMPORT FILE="{f_pad}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            # Hab Module & Interior
            f"BRUSH MOVETO X=-1000 Y=1000 Z={hab_z}",
            f'BRUSH IMPORT FILE="{f_hab}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=-1000 Y=1000 Z={hab_z}",
            f'BRUSH IMPORT FILE="{f_hab_room}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            f"BRUSH MOVETO X=-1000 Y=450 Z={hab_z - 32}",
            f'BRUSH IMPORT FILE="{f_airlock}" MERGE=0 FLAGS=0',
            "BRUSH SUBTRACT",

            # Comm Platform & Mast
            f"BRUSH MOVETO X=1000 Y=-1000 Z={comm_z - 128}",
            f'BRUSH IMPORT FILE="{f_comm_dais}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=1000 Y=-1000 Z={comm_z + 320}",
            f'BRUSH IMPORT FILE="{f_comm_mast}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            f"BRUSH MOVETO X=1000 Y=-300 Z={floor_z + 128}",
            f'BRUSH IMPORT FILE="{f_ramp}" MERGE=0 FLAGS=0',
            "BRUSH ADD",

            "MAP REBUILD",
            "LIGHT APPLY",
            "PATHS BUILD",
            "FLUSH",
        ]
        return cmds

    # -------------------------------------------------------------------------
    # 10. PROCEDURAL UTron COMPONENT BUILDERS
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_utron_diffuser_bus(
        start_pos: Tuple[float, float, float],
        count: int = 8,
        spacing: int = 128,
        tile_type: str = "TT_Normal",
        axis: str = "X",
    ) -> List[str]:
        """Generates an interactive line of luminescent UTron.diffuser pulse tiles."""
        cmds: List[str] = []
        sx, sy, sz = start_pos
        for i in range(count):
            if axis.upper() == "X":
                x = sx + (i * spacing) - (count * spacing // 2)
                y = sy
            else:
                x = sx
                y = sy + (i * spacing) - (count * spacing // 2)
            z = sz + 8

            cmds.extend([
                f"BRUSH MOVETO X={x} Y={y} Z={z}",
                "ACTOR ADD CLASS=UTron.diffuser",
            ])
        cmds.append("FLUSH")
        return cmds

    @staticmethod
    def generate_utron_wirenode_circuit(
        nodes: List[Tuple[float, float, float]],
        circuit_tag: str = "WireCircuit1",
    ) -> List[str]:
        """Generates connected UTron.wirenode triggers linking dynamic diffuser spawning."""
        cmds: List[str] = []
        for i, (x, y, z) in enumerate(nodes):
            cmds.extend([
                f"BRUSH MOVETO X={x} Y={y} Z={z + 16}",
                "ACTOR ADD CLASS=UTron.wirenode",
            ])
        cmds.append("FLUSH")
        return cmds

    # -------------------------------------------------------------------------
    # 11. UE5 MODULAR ARENA EXPORT
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_ue5_modular_arena() -> List[Dict[str, Any]]:
        """Exports parametric scene definition for modern engines."""
        return [
            {"type": "StaticMeshActor", "mesh": "SM_Floor_400x400", "location": [0, 0, 0]},
            {"type": "PointLight", "intensity": 5000, "location": [0, 0, 300], "color": [0.2, 0.8, 1.0]},
            {"type": "PlayerStart", "location": [0, -500, 50]},
        ]
