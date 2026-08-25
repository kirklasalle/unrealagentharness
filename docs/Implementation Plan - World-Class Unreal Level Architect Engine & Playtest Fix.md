# Implementation Plan: World-Class Unreal Level Architect Engine & Playtest Fix

## Problem Statement & Objectives

1. **Desert Arena & World Builds Quality:**
   - The initial "Desert Arena" produced a closed subtractive box with a solid ceiling and basic lighting.
   - For authentic outdoor tournament arenas, the agent must construct open-air arenas with dedicated **SkyBoxes** (`SkyZoneInfo`), atmospheric **Sunlight** (`Engine.Sunlight`), contoured sand/terrain mounds, elevated combat platforms, balanced weapon placements, and safe AI navigation.
2. **Playtest Crash (`Can't find file 'Index.ut2'`):**
   - Clicking the `Play` button failed because `launch_playtest` attempted to load `Index.ut2` without saving the active level to the `Maps/` folder first.
3. **Agent Harness Knowledge & Personality Customization:**
   - The harness requires a full logic and resource knowledge library (`unreal_formulas.py`) defining the exact formulas for Unreal tournament worlds.
   - The user requested agent personality selection in the Settings dialog (Master Architect, UT2004 Veteran Dev, Xan Kriegor AI, Rapid Builder).

---

## Proposed Technical Changes

### 1. Fix Playtest Launch Pipeline

#### [MODIFY] [unrealed_controller.py](file:///g:/UnrealTournament2004/AgentBridge/unrealed_controller.py)
- In `launch_playtest`:
  - When `map_name == "Current"` (default), automatically execute `MAP SAVE FILE="{maps_dir}\AgentPlaytest.ut2"` via UnrealEd command dispatch before launching `UT2004.exe`.
  - Pass `AgentPlaytest.ut2?game={game_type}?NumBots={num_bots}` to `UT2004.exe`.
  - Add fallback validation ensuring the `.ut2` file exists in `Maps/` before spawning the process.

---

### 2. Dedicated SkyBox & Sunlight Engine

#### [MODIFY] [unrealed_controller.py](file:///g:/UnrealTournament2004/AgentBridge/unrealed_controller.py)
- Implement `create_skybox()` method:
  - Carves a subtractive 512x512x512 SkyZone chamber at coordinates `[0, 0, 5000]` far outside playable bounds.
  - Applies thematic sky textures (`AnubisSky`, `SkyBox`, `SkyRenders`, `lavaskyX`).
  - Spawns `Engine.SkyZoneInfo` at `[0, 0, 5000]`.
  - Spawns `Engine.Sunlight` with realistic atmospheric color temperature and brightness in the main playable zone.
  - Configures `FakeBackdrop` surface flags on main ceiling/sky geometry so the skybox is seamlessly projected.

#### [MODIFY] [tools_schema.py](file:///g:/UnrealTournament2004/AgentBridge/tools_schema.py)
- Register `create_skybox` tool schema with parameters for `theme` ('Desert', 'Space', 'Mountain', 'Volcanic', 'Arctic', 'Sunset'), `location`, `dimensions`, and `add_sunlight`.

#### [MODIFY] [server.py](file:///g:/UnrealTournament2004/AgentBridge/server.py)
- Route `create_skybox` tool calls from LLM directly to `controller.create_skybox()`.

---

### 3. Unreal Formula Knowledge Library (`unreal_formulas.py`)

#### [NEW] [unreal_formulas.py](file:///g:/UnrealTournament2004/AgentBridge/unreal_formulas.py)
- Provides standard procedural recipes for UT2004 map creation:
  - **Outdoor Arena Formula:** Main subtractive arena + SkyZone at Z=5000 + Sunlight + central elevated combat platform + 4 sand/rock barriers + 4 PlayerStarts + weapon hierarchy + health/shield caches + path grid.
  - **Interior Fortress Formula:** Main hall + 4 cylinder pillars + adjoining corridor/bunker + torch/fluorescent lighting + defensive posts.
  - **CTF & Domination Formulas:** Symmetrical bases, flag pedestals, domination capture points, jump pads.
  - **Level Design Due Diligence Checklist:** Verified rules for BSP grid snapping, spawn heights (Z=-200/floor), lighting brightness, and navigation density.

---

### 4. Agent Personality & Character Choice

#### [MODIFY] [config_manager.py](file:///g:/UnrealTournament2004/AgentBridge/config_manager.py)
- Add `personalities` dictionary with 4 selectable styles:
  1. `architect`: **Master Level Architect & Designer** (Default) — Authoritative, spatial flow, sightlines, lighting balance.
  2. `veteran`: **Epic Games UT2004 Veteran Dev** — Deep UnrealScript, BSP CSG mechanics, classic UT2004 tournament heritage.
  3. `xan_ai`: **Cybernetic Arena AI (Xan Kriegor)** — Tactical, combat-focused, ruthless arena optimization.
  4. `prototyper`: **Rapid Speed-Builder** — Ultra-concise, hyper-efficient, instantaneous geometry generation.
- Add `active_personality` getter, setter, and persistence.

#### [MODIFY] [llm_engine.py](file:///g:/UnrealTournament2004/AgentBridge/llm_engine.py)
- Dynamically inject the active personality prompt into `SYSTEM_PROMPT` so the agent adopts the user's chosen character voice and technical focus.

#### [MODIFY] [tk_editor_chat.py](file:///g:/UnrealTournament2004/AgentBridge/tk_editor_chat.py)
- Add a **Character Personality** section to the Settings dialog (`⚙ Settings`) with a dropdown, personality descriptions, and live switching.
- Update quick build World category prompts to utilize the new SkyBox, Sunlight, terrain dunes, and elevated combat dais.

---

## Verification Plan

### Automated Tests
1. `python -m py_compile` on all modified/new files.
2. Functional tests for:
   - `controller.create_skybox(theme='Desert')`
   - `controller.launch_playtest(map_name='Current')` (verifying map save to `Maps/AgentPlaytest.ut2`)
   - `config_manager.set_active_personality('veteran')`
   - `llm_engine` dynamic prompt generation with personalities

### Manual Verification
1. Click `Play` in the UnrealEd Cockpit — verify map saves to `Maps/AgentPlaytest.ut2` and UT2004 launches directly into the map without `Index.ut2` errors.
2. Click `Desert Arena` — verify skybox room generated at Z=5000 with `SkyZoneInfo`, Sunlight placed, central platform and dunes generated, PlayerStarts placed, weapon pickups placed, and lighting compiled in seconds.
3. Open `⚙ Settings` — verify Personality selector works and switches character profiles seamlessly.
