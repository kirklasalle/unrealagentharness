"""
Unreal Tournament 2004 (UE2.5) Quick Action Palette for Standalone Agent Harness.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from AgentHarness.core.formula_engine import FormulaEngine


def get_ut2004_palette(
    on_execute_prompt: Optional[Callable[[str], None]] = None,
    system_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Returns UT2004 blueprints and quick action items."""
    return [
        {
            "category": "⚔️ UT2004 Deathmatch & Onslaught",
            "items": [
                {
                    "title": "🏟️ UT2004 Tournament Arena",
                    "desc": "3072x3072 subtractive combat space with center dais and full weaponry.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_arena(system_dir=system_dir),
                    "prompt": "Construct a full UT2004 Deathmatch arena with Shock Rifle, Flak Cannon, and full pathing.",
                },
            ],
        },
        {
            "category": "🔫 UT2004 Weapons & Pickups",
            "items": [
                {
                    "title": "⚡ Shock Rifle Pickup",
                    "desc": "Spawns XWeapons.ShockRiflePickup at builder brush location.",
                    "commands": ["ACTOR ADD CLASS=XWeapons.ShockRiflePickup", "FLUSH"],
                    "prompt": "Place an XWeapons.ShockRiflePickup at the current location.",
                },
                {
                    "title": "💥 Flak Cannon Pickup",
                    "desc": "Spawns XWeapons.FlakCannonPickup at builder brush location.",
                    "commands": ["ACTOR ADD CLASS=XWeapons.FlakCannonPickup", "FLUSH"],
                    "prompt": "Place an XWeapons.FlakCannonPickup at the current location.",
                },
            ],
        },
    ]
