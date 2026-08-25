"""
UT99 GOTY & UTron Mod Quick Action Palette for Standalone Agent Harness.
Provides instant 1-click procedural action buttons for UTron and classic UT99 level builders.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from core.formula_engine import FormulaEngine


def get_ut99_utron_palette(
    on_execute_prompt: Optional[Callable[[str], None]] = None,
    system_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Returns quick-action items formatted for UI button generation."""
    from core.mind_synthesizer import MindSynthesizer

    return [
        {
            "category": "🧠 SOTA MIND-TO-WORLD NEURO SYNTHESIZERS",
            "items": [
                {
                    "title": "🔮 Neuro-Symbolic Cyber Grid Synthesizer",
                    "desc": "Mind-to-World generative compiler: Synthesizes cyberspace platforms, neon light cycle grids, and wirenodes from dynamic intent.",
                    "commands_factory": lambda: MindSynthesizer.synthesize_level_from_mind("UTron Neon Cyberspace Void with floating disc platforms and recognizers", system_dir=system_dir, engine_id="ut99_utron"),
                    "prompt": "Synthesize a UTron cyberspace level with neon disc platforms, wirenode triggers, and identity disc combat armory.",
                },
                {
                    "title": "🏰 Interconnected Multi-Chamber Compound",
                    "desc": "Carves a 3-chamber facility connected via sealed corridors with full weapon armories and pathing.",
                    "commands_factory": lambda: MindSynthesizer.generate_procedural_compound(room_count=3, system_dir=system_dir, engine_id="ut99_utron"),
                    "prompt": "Carve a multi-room interconnected facility with central hub, connecting corridors, and defense perches.",
                },
            ],
        },
        {
            "category": "🌐 UTRON CYBER-GRID BLUEPRINTS",
            "items": [
                {
                    "title": "⚡ Master Control Program (MCP) Core",
                    "desc": "Monumental MCP Sanctum with central rotating core, 4 quadrant platforms, Sentinels, and Armory.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_mcp_core(system_dir=system_dir),
                    "prompt": "Construct the monumental Master Control Program (MCP) Core Sanctum with central rotating core, 4 quadrant platforms, Central_Scrutiniser, wirenodes, weapons, and full pathing.",
                },
                {
                    "title": "🏍️ Light Cycle 90° Grid Arena",
                    "desc": "Generates a 4096x4096 neon circuit grid with cycle morphs, boundary barriers, and cycle spawns.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_lightcycle_grid(system_dir=system_dir),
                    "prompt": "Build a UTron Light Cycle combat arena with 4096x4096 grid dimensions, center obstacle divider, UTron.cycleMorph player starts, perimeter lighting, and rebuild the level.",
                },
                {
                    "title": "🛡️ Discs of Tron (DOT) Arena",
                    "desc": "Builds circular void chamber, floating dais platforms, Identity Discs, and Life Tiles.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_disc_arena(system_dir=system_dir),
                    "prompt": "Build a complete UTron Discs of Tron platform arena with a circular subtractive void chamber, elevated battle platforms, UTron.IdentityDisc spawners, UTron.DiscAmmo pickups, neon cyan lights, and rebuild the level.",
                },
                {
                    "title": "💥 Tank Maze & Combat Grid",
                    "desc": "4096x4096 tactical electronic maze with defensive barrier silos, TankGuns, TankMesh, and Recognizers.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_tank_maze_grid(system_dir=system_dir),
                    "prompt": "Construct an orthogonal UTron Tank Maze arena with circuit barrier walls, TankGuns, Recognizer sentries, and full pathing.",
                },
                {
                    "title": "🛸 Sark's Flagship Carrier Hangar",
                    "desc": "4608x4608 colossal docking hangar with overhead gantry pylons, Drivable Recognizer, and catwalks.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_sarks_carrier(system_dir=system_dir),
                    "prompt": "Construct Sark's Flagship Carrier Hangar with high-level command bridges, Drivable Recognizer, Deadly Discs, and Guard Staffs.",
                },
                {
                    "title": "💡 Diffuser Light Bus (8-Node)",
                    "desc": "Places a line of 8 luminescent diffuser tiles that propagate touch pulses.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_diffuser_bus((0, 0, -200), count=8),
                    "prompt": "Place an 8-tile interactive UTron.diffuser pulse line across the floor at spacing=128 with Baseglow=0.2 and Transfer=0.95, and rebuild the level.",
                },
                {
                    "title": "🔗 Wirenode Spawner Circuit",
                    "desc": "Creates a linked wirenode pair to dynamically spawn glowing diffuser lines.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_wirenode_circuit([(0, 0, -200), (400, 0, -200)]),
                    "prompt": "Spawn two connected UTron.wirenode actors linked via Tag and Event to route dynamic diffuser spawning between (-400,0,0) and (400,0,0).",
                },
            ],
        },
        {
            "category": "⚔️ UTRON WEAPONS & DISC ARMORY",
            "items": [
                {
                    "title": "💿 Deadly Identity Disc",
                    "desc": "Spawns lethal ricocheting UTron.DeadlyDisc.",
                    "commands": ["ACTOR ADD CLASS=UTron.DeadlyDisc", "FLUSH"],
                    "prompt": "Place a UTron.DeadlyDisc weapon pickup at the current location.",
                },
                {
                    "title": "🥏 Identity Disc (Standard)",
                    "desc": "Spawns standard program UTron.IdentityDisc.",
                    "commands": ["ACTOR ADD CLASS=UTron.IdentityDisc", "FLUSH"],
                    "prompt": "Place a UTron.IdentityDisc weapon pickup at the current location.",
                },
                {
                    "title": "⚡ Guard Staff (Electric)",
                    "desc": "Spawns Sark Guard electrified UTron.GuardStaff.",
                    "commands": ["ACTOR ADD CLASS=UTron.GuardStaff", "FLUSH"],
                    "prompt": "Place a UTron.GuardStaff melee weapon pickup at the current location.",
                },
                {
                    "title": "🏑 Jai-Lai Energy Launcher",
                    "desc": "Spawns plasma-bouncing UTron.JaiLai weapon.",
                    "commands": ["ACTOR ADD CLASS=UTron.JaiLai", "FLUSH"],
                    "prompt": "Place a UTron.JaiLai weapon pickup at the current location.",
                },
                {
                    "title": "🔫 MPLP (Multi-Phase Laser)",
                    "desc": "Spawns rapid-fire UTron.MPLP laser pistol.",
                    "commands": ["ACTOR ADD CLASS=UTron.MPLP", "FLUSH"],
                    "prompt": "Place a UTron.MPLP weapon pickup at the current location.",
                },
                {
                    "title": "💣 EMP Shock Grenade",
                    "desc": "Spawns electronic grid-disabling UTron.EMP.",
                    "commands": ["ACTOR ADD CLASS=UTron.EMP", "FLUSH"],
                    "prompt": "Place a UTron.EMP weapon pickup at the current location.",
                },
                {
                    "title": "💥 Tank Heavy Cannon",
                    "desc": "Spawns high-caliber digitized UTron.TankGun.",
                    "commands": ["ACTOR ADD CLASS=UTron.TankGun", "FLUSH"],
                    "prompt": "Place a UTron.TankGun weapon pickup at the current location.",
                },
                {
                    "title": "🔋 Disc Ammo Pack",
                    "desc": "Spawns UTron.DiscAmmo ammunition.",
                    "commands": ["ACTOR ADD CLASS=UTron.DiscAmmo", "FLUSH"],
                    "prompt": "Place a UTron.DiscAmmo pack here.",
                },
            ],
        },
        {
            "category": "🛸 UTRON VEHICLES & RECOGNIZERS",
            "items": [
                {
                    "title": "🔵 Light Cycle (Blue / Flynn)",
                    "desc": "Spawns high-speed Blue Light Cycle UTron.LightCycleB.",
                    "commands": ["ACTOR ADD CLASS=UTron.LightCycleB", "FLUSH"],
                    "prompt": "Place a UTron.LightCycleB vehicle at the current location.",
                },
                {
                    "title": "🔴 Light Cycle (Red / Sark)",
                    "desc": "Spawns high-speed Red Light Cycle UTron.LightCycleR.",
                    "commands": ["ACTOR ADD CLASS=UTron.LightCycleR", "FLUSH"],
                    "prompt": "Place a UTron.LightCycleR vehicle at the current location.",
                },
                {
                    "title": "🟡 Light Cycle (Yellow)",
                    "desc": "Spawns Yellow Light Cycle UTron.LightCycleY.",
                    "commands": ["ACTOR ADD CLASS=UTron.LightCycleY", "FLUSH"],
                    "prompt": "Place a UTron.LightCycleY vehicle at the current location.",
                },
                {
                    "title": "⚡ Power Cycle Heavy",
                    "desc": "Spawns heavy assault UTron.PowerCycle.",
                    "commands": ["ACTOR ADD CLASS=UTron.PowerCycle", "FLUSH"],
                    "prompt": "Place a UTron.PowerCycle vehicle at the current location.",
                },
                {
                    "title": "🛸 Recognizer Patrol Craft",
                    "desc": "Spawns iconic arch-shaped UTron.Recognizer.",
                    "commands": ["ACTOR ADD CLASS=UTron.Recognizer", "FLUSH"],
                    "prompt": "Place a UTron.Recognizer craft at the current location.",
                },
                {
                    "title": "🎮 Drivable Recognizer",
                    "desc": "Spawns player-pilotable UTron.RecoDrivable.",
                    "commands": ["ACTOR ADD CLASS=UTron.RecoDrivable", "FLUSH"],
                    "prompt": "Place a UTron.RecoDrivable pilotable ship at the current location.",
                },
                {
                    "title": "🛡️ Digitized Tank Mesh",
                    "desc": "Spawns grid battle tank UTron.TankMesh.",
                    "commands": ["ACTOR ADD CLASS=UTron.TankMesh", "FLUSH"],
                    "prompt": "Place a UTron.TankMesh vehicle at the current location.",
                },
                {
                    "title": "🛸 Bonus Saucer",
                    "desc": "Spawns aerial scout UTron.BonusSaucer.",
                    "commands": ["ACTOR ADD CLASS=UTron.BonusSaucer", "FLUSH"],
                    "prompt": "Place a UTron.BonusSaucer craft at the current location.",
                },
                {
                    "title": "✈️ Flightator Hovercraft",
                    "desc": "Spawns high-mobility UTron.Flightator.",
                    "commands": ["ACTOR ADD CLASS=UTron.Flightator", "FLUSH"],
                    "prompt": "Place a UTron.Flightator craft at the current location.",
                },
                {
                    "title": "🏍️ Cycle Morph Transformer",
                    "desc": "Spawns UTron.cycleMorph vehicle transformer trigger.",
                    "commands": ["ACTOR ADD CLASS=UTron.cycleMorph", "FLUSH"],
                    "prompt": "Add a UTron.cycleMorph transformer trigger here.",
                },
            ],
        },
        {
            "category": "👾 UTRON CHARACTERS & BOTS",
            "items": [
                {
                    "title": "🔵 Tron (Security Program)",
                    "desc": "Spawns User Champion pawn UTron.Tron.",
                    "commands": ["ACTOR ADD CLASS=UTron.Tron", "FLUSH"],
                    "prompt": "Spawn a UTron.Tron program pawn here.",
                },
                {
                    "title": "🔴 Commander Sark",
                    "desc": "Spawns Grid Commander pawn UTron.Sark.",
                    "commands": ["ACTOR ADD CLASS=UTron.Sark", "FLUSH"],
                    "prompt": "Spawn a UTron.Sark command pawn here.",
                },
                {
                    "title": "🟢 Kevin Flynn (User)",
                    "desc": "Spawns digitized User pawn UTron.Flynn.",
                    "commands": ["ACTOR ADD CLASS=UTron.Flynn", "FLUSH"],
                    "prompt": "Spawn a UTron.Flynn character pawn here.",
                },
                {
                    "title": "🟡 System Guard",
                    "desc": "Spawns command enforcer pawn UTron.Guard.",
                    "commands": ["ACTOR ADD CLASS=UTron.Guard", "FLUSH"],
                    "prompt": "Spawn a UTron.Guard bot enforcer here.",
                },
                {
                    "title": "🟣 Bit Companion",
                    "desc": "Spawns binary pulsing companion UTron.Bit.",
                    "commands": ["ACTOR ADD CLASS=UTron.Bit", "FLUSH"],
                    "prompt": "Spawn a UTron.Bit entity here.",
                },
                {
                    "title": "🐛 Grid Bug Swarm",
                    "desc": "Spawns hostile circuit scavenger UTron.Gridbug.",
                    "commands": ["ACTOR ADD CLASS=UTron.Gridbug", "FLUSH"],
                    "prompt": "Spawn a UTron.Gridbug swarm entity here.",
                },
            ],
        },
        {
            "category": "⚡ UTRON GRID ENTITIES & POWERUPS",
            "items": [
                {
                    "title": "🔋 Life Tile (Health Node)",
                    "desc": "Spawns integrity-restoring floor node UTron.lifetile.",
                    "commands": ["ACTOR ADD CLASS=UTron.lifetile", "FLUSH"],
                    "prompt": "Place a UTron.lifetile health restoration node here.",
                },
                {
                    "title": "🔮 Energy Orb (Power Boost)",
                    "desc": "Spawns high-potency boost sphere UTron.energyorb.",
                    "commands": ["ACTOR ADD CLASS=UTron.energyorb", "FLUSH"],
                    "prompt": "Place a UTron.energyorb boost powerup here.",
                },
                {
                    "title": "⚡ Data Diffuser Tile",
                    "desc": "Spawns interactive data stream node UTron.diffuser.",
                    "commands": ["ACTOR ADD CLASS=UTron.diffuser", "FLUSH"],
                    "prompt": "Place a UTron.diffuser interactive tile here.",
                },
                {
                    "title": "⏱️ Overclocker (Speed Node)",
                    "desc": "Spawns cycle acceleration pickup UTron.overclocker.",
                    "commands": ["ACTOR ADD CLASS=UTron.overclocker", "FLUSH"],
                    "prompt": "Place a UTron.overclocker speed powerup here.",
                },
                {
                    "title": "🎲 Randomiser Modifier",
                    "desc": "Spawns unpredictable disc modifier UTron.randomiser.",
                    "commands": ["ACTOR ADD CLASS=UTron.randomiser", "FLUSH"],
                    "prompt": "Place a UTron.randomiser entity here.",
                },
                {
                    "title": "📡 WireNode Data Conduit",
                    "desc": "Spawns circuit logic intersection UTron.wirenode.",
                    "commands": ["ACTOR ADD CLASS=UTron.wirenode", "FLUSH"],
                    "prompt": "Place a UTron.wirenode conduit actor here.",
                },
                {
                    "title": "🛡️ OmniBlock Force-Barrier",
                    "desc": "Spawns multi-directional defense barrier UTron.OmniBlock.",
                    "commands": ["ACTOR ADD CLASS=UTron.OmniBlock", "FLUSH"],
                    "prompt": "Place a UTron.OmniBlock defense barrier here.",
                },
                {
                    "title": "👁️ Central Scrutiniser Sentinel",
                    "desc": "Spawns overhead grid monitor UTron.Central_Scrutiniser.",
                    "commands": ["ACTOR ADD CLASS=UTron.Central_Scrutiniser", "FLUSH"],
                    "prompt": "Place a UTron.Central_Scrutiniser sentinel here.",
                },
            ],
        },
    ]
