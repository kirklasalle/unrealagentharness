# Unreal Agent Harness: Game Mods & Total Conversions Architecture Guide
### Modular Mod Management, Total Conversion Support & Extensible Mod Registry

**Author:** Kirk LaSalle & Antigravity AI Architect  
**Architecture Version:** v2.9.0  
**Target Engines:** Unreal Engine 1 (UT99 GOTY / OldUnreal 469e), UE2 (UT2004), UE5  
**Workspace:** `G:\UnrealTournament`

---

## 🌐 1. Architecture Overview: Base Engines vs. Game Mods (TC)

In **Unreal Agent Harness**, game systems are categorized into two primary tiers:

```
 Unreal Agent Harness Architecture
 ├── 🎮 Base Game Engines
 │   ├── UT99 GOTY (UE1 / OldUnreal 469e)
 │   ├── UT2003 (UE2.0)
 │   ├── UT2004 (UE2.5 / v3369+)
 │   └── Unreal Engine 5 (UE5.x / Nanite & Lumen)
 │
 └── 📦 Game Mods & Total Conversions (TC)
     ├── ⚡ UTron: Total Conversion Mod (Flagship Tron Cyberspace TC)
     ├── ⚔️ ChaosUT: Evolution Mod (Crossbows, Vortex, Grappling Hooks)
     ├── 🎯 Tactical Ops: Assault on Terror (Tactical CQB TC)
     └── ➕ Custom Game Mods (User-Registered via Harness Cockpit)
```

---

## ⚡ 2. UTron as a Premier Total Conversion Mod

**UTron** is classified as a **Total Conversion (TC) Game Mod** built upon the **UT99 GOTY** engine base:

*   **Category**: `Game Mod (Total Conversion)`
*   **Parent Engine**: `ut99_goty`
*   **Custom Executable Parameters**: `INI=UTronProject.ini USERINI=UTronUser.ini`
*   **Editor Launch Configuration**: `INI=UTronEditor.ini`
*   **Asset Footprint**:
    *   `15` Custom Texture Packages (`UTron_Grids-Lines.utx`, `UTron_Floors-Walls.utx`, `Tron2002.utx`, etc.)
    *   `4` Script Packages (`UTron.u`, `UTronMedia.u`, `UTronMenu.u`, `UTronBrowser.u` — 248 classes)
    *   `5` Sound Packages (`Tron.uax`, `UTronAIvoice.uax`, `UTronVoice.uax`, etc.)
    *   `2` Tracker Soundtracks (`1-Alive.umx`, `Anthem.umx`)
    *   `11` Dedicated Maps (`DOT-Discs-Of-UTron-1.unr`, `DOT-sarkscarrier.unr`, etc.)

---

## ➕ 3. How to Register a New Game Mod in Agent Harness

You can register any new UT99 or UT2004 mod through the **Harness Cockpit UI** or via `config/engine_profiles.json`.

### Option A: Using the Settings Dialog UI
1.  In the Cockpit top bar, click **⚙️ SETTINGS**.
2.  Navigate to the **🎮 Engine Profiles** tab.
3.  Scroll down to **📦 GAME MODS & TOTAL CONVERSIONS (TC)**.
4.  Click **➕ Register New Mod**.
5.  Fill in the Mod Details:
    *   **Mod ID**: e.g., `ut99_chaosut`
    *   **Mod Name**: e.g., `ChaosUT: Evolution Mod`
    *   **Parent Base Engine**: `ut99_goty`
    *   **Editor Launch Args**: `INI=ChaosUTEditor.ini`
    *   **Description**: Features and weapons.
6.  Click **Save Mod**. The new mod immediately becomes selectable in the Target dropdown and settings matrix!

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
  "description": "Classic UT99 weapon and physics total conversion featuring Grappling Hooks, Crossbows, Vortex mines, and Swords.",
  "root_dir": "G:\\UnrealTournament",
  "system_dir": "G:\\UnrealTournament\\System",
  "editor_exe": "UnrealEd.exe",
  "editor_args": "",
  "game_exe": "UnrealTournament.exe",
  "game_args": "INI=UnrealTournament.ini USERINI=User.ini"
}
```

---

## 🎛️ 4. Programmatic Mod Management API (`ConfigManager`)

Developers and scripts can interact with game mods via `AgentHarness.core.config_manager.ConfigManager`:

```python
from AgentHarness.core.config_manager import ConfigManager

cm = ConfigManager()

# Get only Base Game Engines
base_engines = cm.get_base_engines()
# {'ut99_goty': {...}, 'ut2003': {...}, 'ut2004': {...}, 'ue5': {...}}

# Get only Game Mods & Total Conversions
game_mods = cm.get_game_mods()
# {'ut99_utron': {...}, 'ut99_chaosut': {...}, 'ut99_tacticalops': {...}}

# Register a new custom mod
cm.register_game_mod("ut99_infiltration", {
    "name": "Infiltration 2.9 (UE1)",
    "parent_engine": "ut99_goty",
    "icon": "🪖",
    "description": "Realistic tactical firearms simulation mod."
})
```
