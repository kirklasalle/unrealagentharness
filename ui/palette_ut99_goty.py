"""
Unreal Tournament 99 GOTY (UE1 / OldUnreal 469e) Quick Action Palette.
Provides instant 1-click procedural blueprints, weapon armory spawns, powerups, lighting, and path networks.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from AgentHarness.core.formula_engine import FormulaEngine


def get_ut99_goty_palette(
    on_execute_prompt: Optional[Callable[[str], None]] = None,
    system_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Returns category groupings of UT99 GOTY blueprints and quick action commands."""

    return [
        {
            "category": "🏆 UT99 ARENA BLUEPRINTS",
            "items": [
                {
                    "title": "🏟️ Classic Tournament Arena",
                    "desc": "2560x2560 subtractive arena with Shock Rifle, Flak Cannon, Armor, Pillar, Mezzanine, and Pathing.",
                    "commands_factory": lambda: FormulaEngine.generate_ut99_tournament_arena(system_dir=system_dir),
                    "prompt": "Build a classic UT99 Tournament deathmatch arena with Shock Rifle, Flak Cannon, Body Armor, and full Botpack pathing.",
                },
                {
                    "title": "🚩 Dual-Base CTF Outpost (Red)",
                    "desc": "Red Flag Base room with flag dais, sniper perch, weapons, and defensive pathing.",
                    "commands_factory": lambda: FormulaEngine.generate_ut99_ctf_base(system_dir=system_dir, base_color="Red"),
                    "prompt": "Construct a symmetrical UT99 CTF level with Red and Blue flag bases, sniper perches, and midfield path nodes.",
                },
                {
                    "title": "🚩 Dual-Base CTF Outpost (Blue)",
                    "desc": "Blue Flag Base room with flag dais, sniper perch, weapons, and defensive pathing.",
                    "commands_factory": lambda: FormulaEngine.generate_ut99_ctf_base(system_dir=system_dir, base_color="Blue"),
                    "prompt": "Construct a symmetrical UT99 CTF level with Red and Blue flag bases, sniper perches, and midfield path nodes.",
                },
            ],
        },
        {
            "category": "🌲 PREMIER OUTDOOR WORLDS",
            "items": [
                {
                    "title": "🏔️ Verdant Mountain Valley",
                    "desc": "4096x4096 mountain valley with river gorge, stone bridge, fortress bunker, watchtower, pine trees, and boulders.",
                    "commands_factory": lambda: FormulaEngine.generate_ut99_verdant_mountain_valley(system_dir=system_dir),
                    "prompt": "Construct a verdant mountain valley outdoor world with stone fortress, river gorge, stone bridge, watchtower, pine trees, boulders, weapons, and Botpack pathing.",
                },
                {
                    "title": "🏜️ Arid Desert Canyon & Ruins",
                    "desc": "4608x4608 desert canyon with ancient sandstone temple, plateau ramps, colonnades, oasis well, and cacti.",
                    "commands_factory": lambda: FormulaEngine.generate_ut99_desert_canyon_ruins(system_dir=system_dir),
                    "prompt": "Construct an arid desert canyon outdoor world with sandstone temple, colonnades, plateau ramps, oasis well, cacti, and full pathing.",
                },
                {
                    "title": "🌌 Orbital Asteroid Outpost",
                    "desc": "4096x4096 low-gravity asteroid crater with command hab module, comm relay platform, landing pad, and starfield.",
                    "commands_factory": lambda: FormulaEngine.generate_ut99_orbital_asteroid_outpost(system_dir=system_dir),
                    "prompt": "Construct a low-gravity orbital asteroid outpost with hab module, comm relay mast, landing pad, craters, and deep space starfield.",
                },
            ],
        },
        {
            "category": "🔫 UT99 TOURNAMENT WEAPONS",
            "items": [
                {
                    "title": "⚡ Shock Rifle (ASMD)",
                    "desc": "Spawns Botpack.ShockRifle at builder brush location.",
                    "commands": ["ACTOR ADD CLASS=Botpack.ShockRifle", "FLUSH"],
                    "prompt": "Place a Botpack.ShockRifle weapon pickup at the current location.",
                },
                {
                    "title": "💥 Flak Cannon",
                    "desc": "Spawns Botpack.UT_FlakCannon at builder brush location.",
                    "commands": ["ACTOR ADD CLASS=Botpack.UT_FlakCannon", "FLUSH"],
                    "prompt": "Place a Botpack.UT_FlakCannon weapon pickup at the current location.",
                },
                {
                    "title": "🚀 Rocket Launcher (Eightball)",
                    "desc": "Spawns Botpack.UT_Eightball rocket launcher.",
                    "commands": ["ACTOR ADD CLASS=Botpack.UT_Eightball", "FLUSH"],
                    "prompt": "Place a Botpack.UT_Eightball rocket launcher at the current location.",
                },
                {
                    "title": "🎯 Sniper Rifle",
                    "desc": "Spawns Botpack.SniperRifle with headshot capability.",
                    "commands": ["ACTOR ADD CLASS=Botpack.SniperRifle", "FLUSH"],
                    "prompt": "Place a Botpack.SniperRifle at the current location.",
                },
                {
                    "title": "🌪️ Minigun",
                    "desc": "Spawns Botpack.minigun2 high-rate-of-fire weapon.",
                    "commands": ["ACTOR ADD CLASS=Botpack.minigun2", "FLUSH"],
                    "prompt": "Place a Botpack.minigun2 at the current location.",
                },
                {
                    "title": "☢️ Redeemer (Nuclear)",
                    "desc": "Spawns Botpack.WarHeadLauncher super weapon.",
                    "commands": ["ACTOR ADD CLASS=Botpack.WarHeadLauncher", "FLUSH"],
                    "prompt": "Place a Botpack.WarHeadLauncher Redeemer at the current location.",
                },
            ],
        },
        {
            "category": "🛡️ POWERUPS & HEALTH",
            "items": [
                {
                    "title": "🛡️ Shield Belt (150 AP)",
                    "desc": "Spawns Botpack.UT_ShieldBelt golden force field.",
                    "commands": ["ACTOR ADD CLASS=Botpack.UT_ShieldBelt", "FLUSH"],
                    "prompt": "Place a Botpack.UT_ShieldBelt powerup at the current location.",
                },
                {
                    "title": "🟣 Damage Amplifier (UDamage)",
                    "desc": "Spawns Botpack.UDamage 3x damage amplifier.",
                    "commands": ["ACTOR ADD CLASS=Botpack.UDamage", "FLUSH"],
                    "prompt": "Place a Botpack.UDamage amplifier at the current location.",
                },
                {
                    "title": "🧪 Keg of Health (+100 HP)",
                    "desc": "Spawns Botpack.HealthPack (Keg of Health).",
                    "commands": ["ACTOR ADD CLASS=Botpack.HealthPack", "FLUSH"],
                    "prompt": "Place a Botpack.HealthPack (Keg of Health) at the current location.",
                },
                {
                    "title": "🦺 Body Armor (100 AP)",
                    "desc": "Spawns Botpack.Armor2 chest armor.",
                    "commands": ["ACTOR ADD CLASS=Botpack.Armor2", "FLUSH"],
                    "prompt": "Place a Botpack.Armor2 body armor at the current location.",
                },
            ],
        },
        {
            "category": "🧭 BOTPACK NAVIGATION & ZONING",
            "items": [
                {
                    "title": "🚩 PlayerStart (Tournament)",
                    "desc": "Spawns Engine.PlayerStart with default facing.",
                    "commands": ["ACTOR ADD CLASS=Engine.PlayerStart", "FLUSH"],
                    "prompt": "Add an Engine.PlayerStart actor here.",
                },
                {
                    "title": "🌐 PathNode",
                    "desc": "Spawns an Engine.PathNode actor for Botpack AI bot pathing.",
                    "commands": ["ACTOR ADD CLASS=Engine.PathNode", "PATHS BUILD", "FLUSH"],
                    "prompt": "Add an Engine.PathNode navigation node actor here.",
                },
                {
                    "title": "💧 ZoneInfo",
                    "desc": "Adds Engine.ZoneInfo for fluid physics or damage.",
                    "commands": ["ACTOR ADD CLASS=Engine.ZoneInfo", "FLUSH"],
                    "prompt": "Add an Engine.ZoneInfo actor configured for water/slime zoning.",
                },
                {
                    "title": "🌌 SkyZoneInfo (Parallax Skybox)",
                    "desc": "Configures a 3D skybox anchor for cosmic backgrounds.",
                    "commands": ["ACTOR ADD CLASS=Engine.SkyZoneInfo", "FLUSH"],
                    "prompt": "Create a SkyZoneInfo skybox chamber with distant stars and nebula.",
                },
            ],
        },
    ]
