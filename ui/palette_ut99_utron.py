"""
UT99 GOTY & UTron Mod Quick Action Palette for Standalone Agent Harness.
Provides instant 1-click procedural action buttons for UTron and classic UT99 level builders.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from AgentHarness.core.formula_engine import FormulaEngine


def get_ut99_utron_palette(
    on_execute_prompt: Optional[Callable[[str], None]] = None,
    system_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Returns quick-action items formatted for UI button generation."""
    return [
        {
            "category": "⚡ UTron Cyber-Grid Blueprints",
            "items": [
                {
                    "title": "🔴 Discs of Tron Arena",
                    "desc": "Builds circular void chamber, floating dais platforms, and Identity Discs.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_disc_arena(system_dir=system_dir),
                    "prompt": "Build a complete UTron Discs of Tron platform arena with a circular subtractive void chamber, elevated battle platforms, UTron.IdentityDisc spawners, UTron.DiscAmmo pickups, neon cyan lights, and rebuild the level.",
                },
                {
                    "title": "🏍️ Light Cycle 90° Arena",
                    "desc": "Generates a 3072x3072 grid with cycle morphs and boundary barriers.",
                    "commands_factory": lambda: FormulaEngine.generate_utron_lightcycle_grid(system_dir=system_dir),
                    "prompt": "Build a UTron Light Cycle combat arena with 3072x3072 grid dimensions, center obstacle divider, UTron.cycleMorph player starts, perimeter lighting, and rebuild the level.",
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
            "category": "🕹️ UTron Signature Pickups & Pawns",
            "items": [
                {
                    "title": "🥏 Identity Disc Weapon",
                    "desc": "Spawns UTron.IdentityDisc at builder brush location.",
                    "commands": ["ACTOR ADD CLASS=UTron.IdentityDisc", "FLUSH"],
                    "prompt": "Place a UTron.IdentityDisc pickup here.",
                },
                {
                    "title": "🔋 Disc Ammo Pack",
                    "desc": "Spawns UTron.DiscAmmo pickup.",
                    "commands": ["ACTOR ADD CLASS=UTron.DiscAmmo", "FLUSH"],
                    "prompt": "Place a UTron.DiscAmmo pack here.",
                },
                {
                    "title": "🏍️ Cycle Morph Trigger",
                    "desc": "Spawns UTron.cycleMorph player vehicle transformer.",
                    "commands": ["ACTOR ADD CLASS=UTron.cycleMorph", "FLUSH"],
                    "prompt": "Add a UTron.cycleMorph transformer trigger here.",
                },
            ],
        },
    ]
