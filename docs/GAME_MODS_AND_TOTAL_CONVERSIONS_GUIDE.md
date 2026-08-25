# Unreal Agent Harness: Game Mods & Total Conversions Architecture Guide
### Modular Mod Management, Total Conversion Support & Universal Mod Registry

**Author:** Kirk LaSalle & Antigravity AI Engineering  
**Architecture Version:** v3.1.0  
**Target Engines:** Unreal Engine 1 (UT99 GOTY / OldUnreal 469e), UE2 (UT2004), UE5  
**Official Repository:** [https://github.com/kirklasalle/unrealagentharness](https://github.com/kirklasalle/unrealagentharness)

---

## 🌐 1. Architecture Overview: Base Engines vs. Universal Game Mods (TC)

In **Unreal Agent Harness**, game systems are categorized into two primary tiers:

```
 Unreal Agent Harness Architecture
 ├── 🎮 Base Game Engines
 │   ├── Unreal (1998 Namesake / UE1)
 │   ├── UT99 GOTY (UE1 / OldUnreal 469e)
 │   ├── UT2003 (UE2.0)
 │   ├── UT2004 (UE2.5 / v3369+)
 │   └── Unreal Engine 5 (UE5.x / Nanite & Lumen)
 │
 └── 📦 Universal Game Mods & Total Conversions (TC)
     ├── ⚔️ ChaosUT: Evolution (Crossbows, Vortex Cannons, Proxy Mines, Grappling Hooks)
     ├── 🎯 Tactical Ops: Assault on Terror (Tactical CQB, Real-World Weapons, Rescue Spawns)
     ├── 🪖 Infiltration (Ultra-Realistic Tactical Military Combat & Aim-Down-Sights)
     ├── 👾 Monster Hunt (Cooperative PVE Boss Hunts & Dungeon Progression)
     ├── 🔒 Jailbreak (Cooperative Capture & Release Team Gameplay)
     ├── 🚀 Rocket Arena (Pure Clan Combat & 1v1 Skill Arenas)
     └── ➕ Custom Game Mods & Mutators (User-Registered via Harness Cockpit)
```

---

## ⚔️ 2. Universal Mod Registry & Architectural Principles

Unreal Agent Harness provides first-class support for any game mod or total conversion across the Unreal spectrum:

*   **Modular Profile Architecture**: Every mod can declare custom `.ini` files, custom package lists (`.u`, `.utx`, `.uax`, `.umx`), and custom UCC compile chains.
*   **Zero Hardcoding**: Mods inherit all base engine functionality (CSG carving, lighting, AI pathing) while overriding weapon tables, player start classes, and navigation behaviors.
*   **Non-Destructive Workflows**: Mod assets are compiled and packaged without altering stock engine files.

### Key Mod Archetypes Supported:
1. **Weapon & Physics Overhauls** (*ChaosUT*): Custom melee weapons, proxy mine navigation behaviors, anti-gravity jump pads.
2. **Tactical & Realistic Conversions** (*Tactical Ops*, *Infiltration*): Buy zones, bomb defusal objectives, hostage pathing nodes.
3. **PVE & Cooperative Gametypes** (*Monster Hunt*, *Invasion*): Monster spawning triggers, cooperative objective checkpoints, boss encounter arenas.
4. **Arena Combat & Tournaments** (*Rocket Arena*, *Jailbreak*): Dual-cage jail release triggers, arena teleport switches, clan spectator perches.

---

## ➕ 3. How to Register a New Game Mod in Agent Harness

You can register any new UT99, UT2004, or custom community mod through the **Harness Cockpit UI** or via `config/engine_profiles.json`.

### Option A: Using the Cockpit Settings UI
1. In the Cockpit top bar, click **⚙️ SETTINGS**.
2. Navigate to the **🎮 Engine Profiles** tab.
3. Scroll to **📦 GAME MODS & TOTAL CONVERSIONS (TC)**.
4. Click **➕ Register New Mod**.
5. Fill in the Mod Details:
   * **Mod ID**: e.g., `ut99_chaosut`
   * **Mod Name**: e.g., `ChaosUT: Evolution Mod`
   * **Parent Base Engine**: `ut99_goty`
   * **Editor Launch Args**: `INI=ChaosUTEditor.ini`
   * **Description**: Custom weapons, gametypes, and items.
6. Click **Save Mod**. The new mod immediately becomes selectable across all tools and scripts!

### Option B: JSON Profile Registration (`config/engine_profiles.json`)
```json
"ut99_chaosut": {
  "id": "ut99_chaosut",
  "name": "ChaosUT: Evolution Mod (UE1 / 469e)",
  "category": "Game Mod (Total Conversion)",
  "mod_type": "Total Conversion",
  "parent_engine": "ut99_goty",
  "generation": "UE1",
  "icon": "⚔️",
  "description": "Classic UT99 weapon and physics total conversion featuring Grappling Hooks, Crossbows, Vortex mines, and Melee Arenas.",
  "root_dir": "G:\\UnrealTournament",
  "system_dir": "G:\\UnrealTournament\\System",
  "editor_exe": "UnrealEd.exe",
  "editor_args": "INI=ChaosUT.ini",
  "game_exe": "UnrealTournament.exe",
  "game_args": "INI=ChaosUT.ini USERINI=ChaosUser.ini"
}
```

---

## 🎛️ 4. Programmatic Mod Management API (`ConfigManager`)

Developers and scripts can query and manipulate registered mods using `core.config_manager.ConfigManager`:

```python
from AgentHarness.core.config_manager import ConfigManager

cm = ConfigManager()

# Get only Base Game Engines
base_engines = cm.get_base_engines()
# {'ut99_goty': {...}, 'ut2003': {...}, 'ut2004': {...}, 'ue5': {...}}

# Get registered Total Conversions & Mods
game_mods = cm.get_game_mods()
# {'ut99_chaosut': {...}, 'ut99_tacticalops': {...}}

# Dynamically register a new mod
cm.register_game_mod(
    mod_id="ut99_monsterhunt",
    name="Monster Hunt Co-Op",
    parent_engine="ut99_goty",
    description="PVE Co-Op Campaign Mod with custom monster triggers."
)
```
