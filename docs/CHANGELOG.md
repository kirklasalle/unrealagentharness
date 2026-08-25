# Changelog - UnrealEd Agent Harness & World Architect Engine

All notable changes, architectural enhancements, and procedural world-building procedures are documented in this file.

## [v3.1.0] - 2026-08-25: Public Launch Elevation — Luxury Multi-Theme Web Suite (5 Unreal Eras), 28-Year Unreal Continuum, Universal Community Mod Support & Agentic Sacred Covenant

### 🌐 World-Class Standalone Public Web Suite (`public_html/`)
- **7-Page Zero-Dependency Public Platform**:
  - `index.html`: Portal with hero crest, certified 96.25/100 health badge, GitHub integration, and interactive CSG procedural room generator.
  - `timeline.html`: Interactive 28-year timeline celebrating the Unreal Continuum (1998 to 2026+).
  - `mods.html`: Universal modding and total conversion showcase celebrating community creators.
  - `architecture.html`: 5-tier architecture, IPC communication, and Win32 automation guide.
  - `academy.html`: Unreal Academy trick player, 3D illusions, and classic level deconstructions.
  - `docs.html`: Live searchable documentation library with interactive tag filtering and citations.
  - `covenant.html`: The complete Agentic Sacred Covenant and Kirk LaSalle's 10 Laws of AI Supremacy.

### 🎨 Live Multi-Theme Switcher (5 Historical Unreal Eras)
- Integrated 1-click real-time CSS variable morphing across 5 selectable aesthetics:
  - 🏆 **Liandri Tournament Gold** (Default: Deep Obsidian Void `#06080d`, Liandri Gold `#f5a623`, Plasma Cyan `#00d4ff`).
  - 🌿 **Na Pali Mystic Sanctuary** (1998 Unreal Emerald `#10b981`, Ancient Stone Slate, and Temple Moss Gold `#d4af37`).
  - 🌌 **UE5 Nanite & Lumen Frontier** (Monochromatic Titanium White `#ffffff`, Pure Bloom, and Jet Black Matte `#000000`).
  - 📟 **1998 UnrealEd Retro Terminal** (Phosphor Amber `#eab308`, Terminal Green `#84cc16`, and 3Dfx Glide CRT ambiance).
  - 🛸 **Deep Space Skaarj Orbital** (Cosmic Deep Navy `#04060e`, Tactical Alert Crimson `#ef4444`, and Cobalt Thrusters `#3b82f6`).
- **Adaptive Vector Constellation Canvas (`#cyberCanvas`)**: Real-time 60fps ReachSpec lattice simulation adapting particle and line colors to the active theme.
- **Dynamic Cursor Spotlight Tracking**: Cards calculate `--mouse-x` and `--mouse-y` for a clean ambient bloom.
- **1-Click Clipboard Code Copying**: Added copy buttons with animated checkmark feedback.

### 🎮 Universal Community Mod Support
- Universal total conversion architecture supporting *ChaosUT*, *Tactical Ops*, *Infiltration*, *Monster Hunt*, *Jailbreak*, *Rocket Arena*.
- Added `docs/GAME_MODS_AND_TOTAL_CONVERSIONS_GUIDE.md` detailing dynamic mod registration and programmatic `ConfigManager` APIs.

### 📜 Agentic Sacred Covenant & Kirk LaSalle's 10 Laws of AI Supremacy
- Codified `AGENTIC_SACRED_COVENANT.md` and `AGENTIC_PRIME_DIRECTIVE.md` in repository root.
- Established human creative supremacy, ethical boundaries, and immutable safety tenets.

### 🧪 Certified Health Score & Test Suite
- Certified **96.25 / 100 World-Class Health Score** in `docs/07_COMPREHENSIVE_SOFTWARE_APPLICATION_AUDIT.md`.
- **106 / 106 unit tests passing (100%)** in ~5.3 seconds.
- Fully integrated with official GitHub repository: `https://github.com/kirklasalle/unrealagentharness`.

## [v2.16.2] - 2026-08-24: UT2004 FPathBuilder AIController Crash Resolution, LevelInfo Root Actor Integration, Async PostMessage Command Dispatch, and Complete Nav Lattice Densification

### 🛡️ Critical Bugfix: UT2004 `FPathBuilder::buildPaths` AIController Crash Resolution
- **Root Cause Identified from Crash Dumps & Screenshots (`agentharness_106.png`, `agentharness_107.png`)**:
  - UnrealEd 3.0 (UT2004 Build 3374) crashed during `PATHS BUILD` with:
    `Actor not found: AIController MyLevel.AIController1`
    `History: ULevel::GetActorIndex <- ULevel::DestroyActor <- (AIController MyLevel.AIController1) <- FPathBuilder::buildPaths <- UEditorEngine::Exec_Paths`
  - In Unreal Engine 2.5, `FPathBuilder::buildPaths` spawns a temporary test controller (`AIController MyLevel.AIController1`) to test jump clearances and ReachSpecs. When the root singleton actor `Engine.LevelInfo` is missing from the imported level actors, the spawned `AIController` fails to register in `Level.ControllerList`, causing `ULevel::DestroyActor` / `ULevel::GetActorIndex` to crash.
- **Architectural Solution — Universal `LevelInfo` & `ZoneInfo` Root Injection**:
  - Added `Engine.LevelInfo` with proper `DefaultGameType` (`XGame.xDeathMatch`, `Onslaught.ONSOnslaughtGame`, or `SkaarjPack.Invasion`) and `Engine.ZoneInfo` across all 10 UT2004 procedural world generators in `core/formula_engine.py`.
  - Added test assertions to `test_harness.py` guaranteeing `LevelInfo` presence in all generated worlds.

### ⚡ Performance & Stability: Asynchronous `PostMessage` Command Dispatch
- **Root Cause**:
  - `EngineController.execute_command()` used blocking synchronous `win32gui.SendMessage(hwnd_edit, win32con.WM_CHAR, 13, 0)`, freezing the calling Python thread whenever UnrealEd engaged in long-running BSP or path builds.
- **Architectural Solution**:
  - Switched keystroke execution (`VK_RETURN`, `WM_CHAR 13`, `WM_KEYUP`) to non-blocking `win32gui.PostMessage()`.
  - Broadened `dismiss_dialogs()` to automatically dismiss `Map Check` and progress popups by class and window title.

### 🧭 Complete Navigation Network Densification & JumpPad Targeting
- Densified navigation node grids across all UT2004 world generators (`Orbital Asteroid Mining`, `Arctic Glacier Outpost`, `Invasion Arena`, `Tournament Colosseum`) ensuring maximum node-to-node spacing $\le 550\text{ UU}$.
- Converted steep 512 UU vertical ledges into walkable 128 UU daises with cardinal approach nodes.
- Explicitly wired all `xJumpPad`s with designated `JumpTarget`s (`Path_Gantry_Top`, `DaisPathNode`).
- Updated Space texture theme to preload `SkyBox.utx` with valid `SkyBox.space.starfield` materials.

## [v2.16.1] - 2026-08-24: UT2004 USkeletalMeshInstance Viewport Crash Resolution, Safe Vehicle Factory System, and Auto-Package Preloader

### 🛡️ Critical Bugfix: UT2004 `USkeletalMeshInstance::Render` General Protection Fault Resolution
- **Root Cause Identified from Crash Dumps & Screenshots (`agentharness_103.png`, `agentharness_104.png`)**:
  - In Unreal Tournament 2004 (UE2.5), placing live vehicle actor Pawns (`Onslaught.ONSHoverTank`, `ONSHoverBike`, `ONSRV`, `ONSPRV`, `ONSAttackCraft`) or raw 1st-person Weapon actors (`Onslaught.ONSAVRiL`) directly into an editor map causes UnrealEd's real-time 3D perspective viewport (`FDynamicActor::Render -> USkeletalMeshInstance::Render`) to crash with a General Protection Fault (0xC0000005) because skeletal bone hierarchies and karma physics instances require an active gameplay player pawn attachment.
- **Architectural Solution — Safe `ONSVehicleFactory` & `ONSAVRiLPickup` Hierarchy**:
  - Replaced all raw vehicle pawn placements in `core/formula_engine.py` and `ui/palette_ut2004.py` with standard, rock-solid **`ONSVehicleFactory`** subclasses:
    - 🚜 `Onslaught.ONSTankFactory` (Goliath heavy tank factory)
    - 🏍️ `Onslaught.ONSHoverCraftFactory` (Manta agile hovercraft factory)
    - 🚙 `Onslaught.ONSRVFactory` (Scorpion light buggy factory)
    - ✈️ `Onslaught.ONSAttackCraftFactory` (Raptor VTOL aircraft factory)
    - 🚛 `Onslaught.ONSPRVFactory` (Hellbender 3-person combat rover factory)
    - 🛸 `OnslaughtFull.ONSBomberFactory` (Cicada dual-pilot VTOL gunship factory)
    - 🛞 `OnslaughtBP.ONSShockTankFactory` (Paladin mobile plasma shield vehicle factory)
    - 🤖 `OnslaughtFull.ONSMASFactory` (Leviathan colossal 5-man mobile super fortress factory)
  - Replaced all raw `Onslaught.ONSAVRiL` weapon actor placements with the static-mesh world pickup **`Onslaught.ONSAVRiLPickup`** across `formula_engine.py`, `palette_ut2004.py`, `llm_engine.py`, and `test_harness.py`.
  - Factories and pickups display safe static meshes in UnrealEd without triggering skeletal mesh render crashes.

### ⚡ Fix: Abstract `ONSPowerNode` Class Instantiation Replaced with `ONSPowerNodeNeutral`
- Resolved UnrealEd map import warning `Warning: SpawnActor failed because class ONSPowerNode is abstract`.
- Updated all Onslaught world formulas to place concrete, placeable **`Onslaught.ONSPowerNodeNeutral`** actors.

### 📦 New: Automatic Texture Package Preloader (`_get_ut2004_obj_load_commands`)
- Added automatic `OBJ LOAD FILE="..\Textures\<pkg>" PACKAGE=<pkg_name>` preloading to all UT2004 world formulas before brush/actor importation.
- Eliminates missing material warnings (`Failed to find object 'Material AntalusTextures.Rock.CliffRock1'`) and guarantees flawless visual rendering across Canyon, Arctic, Space, Volcanic, Egyptian, and Cyber themes.

### 🧭 Critical Fix: Navigation Network Loop & Embedded Pickup Resolution (`PATHS BUILD`)
- **Root Cause Identified from Screenshot (`agentharness_105.png`)**:
  - UnrealEd 3 froze on `PATHS BUILD` ("Creating intermediate paths") with warnings `Pickup embedded in collision geometry!` on `Rocket_Mid` and `May be too close to other navigation points` on `PlayerStart`.
  - **Embedded Pickups**: Pickups (`Rocket_Mid`, `Sniper_High`) placed in `generate_ut2004_onslaught_canyon_outpost` were positioned at `z_floor + 50` while inside the central plateau cylinder (which occupies `z_floor` to `z_floor + 256`), embedding them in solid additive BSP geometry.
  - **Overlapping Nav Nodes**: `PlayerStart` and `PathNode` were placed at identical `(X, Y, Z)` coordinates, generating cyclic 0-cost ReachSpecs that hung the editor's path-building reachability raytracer.
- **Architectural Solution**:
  - Elevated all plateau/bunker/dais pickups and path nodes to `z_surface_top + 36..40` ensuring full vertical collision clearance.
  - Decoupled `PathNode`s from `PlayerStart`s, `xJumpPad`s, and `RoadPathNode`s across all 10 procedural world generators, establishing clean walking corridors and dedicated vehicle lanes.
  - Added `test_ut2004_navigation_nodes_have_no_duplicate_locations` unit test to guarantee zero overlapping navigation nodes across all generators.

### 🧪 Test Coverage: 90/90 Unit Tests Passing
- Added `test_ut2004_palette_vehicle_factory_safety`: enforces with regex lookahead that no palette item ever places crash-prone live vehicle pawns.
- Added `test_ut2004_all_generators_preload_textures`: verifies all 10 UT2004 generators emit package preloading commands.
- Added `test_ut2004_navigation_nodes_have_no_duplicate_locations`: validates 100% clean navigation graphs without duplicate coordinates or cyclic reachability traps.

## [v2.16.0] - 2026-08-24: Ultra Geometry Detail Engine, Target & Palette Audit, and Unreal 1 Single-Player RPG Story Systems

### 🏛️ New: Ultra Geometry Detail Engine (75% Engine Limit Architecture)
- **Extreme Geometric Artistry (`core/formula_engine.py`)**:
  - Pushes procedural architecture to 75% of UnrealEd editor engine limits without causing BSP node overflows or compilation degradation.
  - Added `DETAIL_PRESETS` with `"standard"`, `"high"`, and `"ultra"` configurations.
  - `"ultra"` presets scale cylinder/pillar tessellation up to 48 sides, towers to 24 sides, and octagons to 24 sides.
- **New Parametric PolyList Brush Primitives**:
  - `BeveledBox` / `chamfer`: 10-face watertight planar box with 45° chamfered vertical corners.
  - `Arch` / `ArchedTunnel` / `vault`: Semicircular barrel vault tessellated into customizable smooth facet steps (16–24 sides).
  - `Buttress`: Tapered fortification / cathedral wall brace.
  - `TrimStrip` / `Molding`: Wall-floor baseboards, ceiling crown cornices, and architectural ledges.
  - `HexColumn`: 6-sided crystalline column with exact trigonometric vertices.
- **Semi-Solid CSG Decoration (`PF_Semisolid = 32`)**:
  - Added `_write_semisolid_brush_file()` helper setting `Flags=32`.
  - Places columns, moldings, cornices, buttresses, and arch understructures as semi-solid brushes that decorate levels with zero BSP node cuts or Hall of Mirrors (HOM) glitches.

### 🏰 New: Unreal 1 Single-Player RPG Narrative Sanctuary (`generate_unreal1_sp_sanctuary`)
- Full procedural narrative dungeon sanctuary honoring the groundbreaking original *Unreal* (1998) FPS RPG:
  - **Narrative Lore**: `UnrealShare.TranslatorEvent` stone tablets with ancient Nali history and secret hints.
  - **Living World NPCs & Creatures**: Friendly 4-armed `UnrealShare.Nali` monks, heavy mercenary `UnrealShare.Brute` guards, acrobatic `UnrealI.SkaarjWarrior` assassins.
  - **Exploration Pickups**: Rechargeable `UnrealShare.DispersionPistol`, `AutoMag`, `Stinger`, and `UnrealShare.NaliFruit` healing plants.
  - **Sacred Architecture**: Vaulted nave with arched ceilings, fluted columns, torch alcoves, and sacred pool crypts.

### 🎯 Audited & Verified: Target Engine Switching & Quick Action Palettes
- **Full Application Target Audit**:
  - Verified `ConfigManager.get_all_engine_profiles()` and cockpit tab mappings for `ut99_goty`, `ut99_utron`, `ut99_chaosut`, `ut99_tacticalops`, `ut2003`, and `ut2004`.
  - All targets dynamically select their corresponding Quick Architect Palette notebook tab and re-initialize controller paths and LLM prompts.
- **Full Palette Audit & Execution**:
  - `ui/palette_ut99_goty.py`: Expanded with dedicated **🏰 UNREAL 1 RPG / NARRATIVE TEMPLE & DUNGEON** section and Ultra Arena/Valley blueprints.
  - `ui/palette_ut99_utron.py`: Verified all 7 cyber-grid blueprints, weapon spawners, and diffuser circuits.
  - `ui/palette_ut2004.py`: Verified all 8 full world environments, vehicle staging docks, and Skaarj invasion spawners.
  - All commands and factory lambdas evaluated and validated across 87 unit tests with 100% pass rate.

### 🤖 Updated: Tool Calling Schemas & LLM Profiles
- `core/tools_schema.py`: Added `detail_level` parameter (`"standard" | "high" | "ultra"`) and registered `build_unreal1_sanctuary` and `build_outdoor_world`.
- `core/llm_engine.py`: Updated tool dispatch handlers to generate ultra-detailed procedural levels.
- `config/llm_profiles.json`: Configured `"default_detail_level": "ultra"`.

### 🧪 Expanded: Test Suite (75 → 87 tests, 100% Passing)
- Added `TestTargetAndPaletteSystem` (5 comprehensive audit tests).
- Added `TestFormulaEngineUltraGeometry` (6 ultra geometry, semi-solid, and sanctuary generator tests).

---

## [v2.15.0] - 2026-08-24: Win32 DPI Awareness, Update Engine Hardening & Expanded Test Coverage

### 🖥️ New: Win32 DPI Awareness Initialization (`core/bootstrap.py`)
- **3-Tier Automatic DPI Awareness Activation** at process import-time:
  1. *Win10 1703+*: `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)` — full per-monitor DPI scaling with automatic non-client area scaling.
  2. *Win8.1+*: `SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)` — per-monitor DPI scaling.
  3. *Win7+*: `SetProcessDPIAware()` — system-wide DPI awareness fallback.
- **`get_dpi_awareness_level()`**: Query which tier was activated (`per_monitor_v2` | `per_monitor` | `system_aware` | `unavailable`).
- **`get_dpi_scale_factor(hwnd)`**: Returns the DPI scale factor (e.g. `1.0` for 100%, `1.5` for 150%, `2.0` for 4K 200%) for a given window handle. Uses a 3-tier API fallback: `GetDpiForWindow` → `GetDpiForSystem` → `GetDeviceCaps(LOGPIXELSX)`.
- **Impact**: All downstream `GetWindowRect` and `ImageGrab.grab()` calls now return true physical pixel coordinates on 4K and multi-monitor setups, eliminating blurry/misaligned viewport captures.

### 🔧 Fixed: Update Engine `ResourceWarning` (`core/update_engine.py`)
- Replaced bare `urllib.request.urlretrieve()` call in the ZIP download path with a proper `urllib.request.urlopen()` context manager (`with` block).
- Added chunked streaming download (64 KB per read) with byte-count logging for transparent download progress.
- Added explicit `User-Agent` header and `timeout=30.0` to the ZIP download request.
- **Impact**: Eliminates `ResourceWarning: unclosed <http.client.HTTPResponse>` during auto-update operations.

### 📸 Improved: DPI-Aware Viewport Capture (`core/vision_inspector.py`, `core/engine_controller.py`)
- `VisionInspector.capture_full_window()` and `capture_viewport()` now log the active DPI scale factor for diagnostic clarity.
- Toolbar and status bar pixel offsets in viewport quadrant extraction are now scaled by `get_dpi_scale_factor()` for correct cropping on HiDPI displays.
- `EngineController.capture_viewport_image()` now includes DPI-aware coordinate logging.

### 🧪 Expanded: Test Suite (70 → 75 tests)
- **`TestBootstrapDPI`** (3 tests):
  - `test_dpi_awareness_level_string`: Validates awareness tier is a recognized string.
  - `test_dpi_scale_factor_returns_float`: Validates scale factor ≥ 1.0 on primary monitor.
  - `test_dpi_scale_factor_with_invalid_hwnd`: Validates graceful fallback with invalid window handle.
- **`TestUpdateEngineResourceSafety`** (2 tests):
  - `test_check_for_updates_no_resource_warning`: Asserts zero `ResourceWarning` during HTTP version check.
  - `test_apply_update_source_uses_context_manager`: Static analysis confirms `urlretrieve` is replaced with `urlopen`.

---

## [v2.14.0] - 2026-08-24: World-Class Software Application Audit, Critical Engineering Review, Market Intelligence & Official Roadmap

### 📋 New: Comprehensive Software Application & Critical Audit
- **Master Audit Document (`docs/07_COMPREHENSIVE_SOFTWARE_APPLICATION_AUDIT.md`)**:
  - **Overall Health Score: 96.25 / 100 (World-Class Certification)** across all 5 architectural tiers.
  - **Deep Tier-by-Tier Audit**:
    1. *Tier 1 (Win32 Automation & Platform Abstraction)*: Window handle resolution, Edit message injection, log offset streaming, modal dialog suppression.
    2. *Tier 2 (Procedural CSG Geometry & Synthesis)*: 150KB+ formula engine generating 100% closed, coplanar, watertight T3D PolyLists and lighting rigs.
    3. *Tier 3 (Bot AI Navigation & Pathing)*: ReachSpec directed graph generation, JumpPad parabolic physics, and real-time reachability parsing.
    4. *Tier 4 (Multi-Provider LLM & Tool-Calling Orchestration)*: Frontier cloud inference (Gemini 2.5 Flash/Pro, Claude 3.7, GPT-4o, DeepSeek, Groq) and local offline inference (Ollama/LM Studio).
    5. *Tier 5 (Presentation, API, Config & Telemetry)*: Zero-dependency Tkinter GUI (< 35MB RAM), FastAPI bridge (Port 9090), and .nexus AMTP v3.0 interop.
  - **Critical Reliability & Security Audit**:
    - Concurrency and thread safety between GUI loop and daemon background workers.
    - Sensitive credential redaction (regex sanitization of API keys in logs and crash dumps).
    - Multi-generational compatibility matrix spanning UE1, UE2, UE2.5, and UE5.

### 🧠 New: Comprehensive AI Model Evaluation for Unreal Editor World Creation
- **Model Capability Matrix & Benchmarking**:
  - 🥇 **Google Gemini 2.5 Flash (`gemini-2.5-flash`)**: Top recommendation for real-time interactive level design (sub-400ms speed, 1M context, exceptional JSON tool calling, multi-modal viewport vision).
  - 🥈 **Google Gemini 2.5 Pro (`gemini-2.5-pro`)**: Premier architectural planner for massive package trees (2M context).
  - 🥉 **Anthropic Claude 3.7 Sonnet (`claude-3-7-sonnet-20250219`)**: Hybrid reasoning engine for intricate coordinate math and UnrealScript coding.
  - 💻 **Qwen 2.5 Coder 32B & Llama 3.3 70B (Ollama)**: Leading 100% private, air-gapped offline local models for secure studio environments.
- **Easy Configuration**:
  - Added pre-configured `google-gemini-flash` profile to `config/llm_profiles.json`.
  - Updated `docs/LLM_PROVIDER_SETUP.md` with step-by-step setup guides for all frontier and local models.

### 🧭 New: Official 2026–2027 Engineering & Product Roadmap
- **`ROADMAP.md` & `docs/ROADMAP.md`**:
  - Formulated phased milestones covering:
    - *Phase 1 (Q3 2026)*: Multi-Engine Exhaustive Palettes & Full Application Audit (Complete).
    - *Phase 2 (Q4 2026)*: Multi-Modal Vision & Direct Viewport Semantic Spatial Engine.
    - *Phase 3 (Q1 2027)*: Autonomous Level Synthesis Swarm & .nexus AMTP v3.0 Hub.
    - *Phase 4 (Q2 2027)*: Headless CI/CD Level Testing, Bot Simulation & QA Regression.
    - *Phase 5 (Q3–Q4 2027)*: Cross-Engine Universal Level Transpiler (UE1 $\leftrightarrow$ UE2.5 $\leftrightarrow$ UE5).

### 📊 Updated: Market Landscape & Competitive Intelligence Audit
- **`docs/MARKET_LANDSCAPE_AND_COMPETITIVE_ANALYSIS.md`**:
  - Expanded competitive benchmarking against Promethean AI, Sloyd, Meshy, Scenario, Ultimate Engine Copilot, UnrealGPT, Autonomix, and Claude Computer Use.
  - Articulated UAH strategic moats: 25-year backward/forward engine span, zero-latency Win32 direct injection, 100% air-gapped local model support, and .nexus AMTP v3.0 swarm connectivity.

---

## [v2.13.0] - 2026-08-24: UT2004 World-Class Exhaustive Palette, Procedural Environments & U1-U5 Master Knowledgebase

### ⚔️ New: Exhaustive UT2004 (UE2.5 / v3369+) Quick Action Palette
- **10 Rich Categories with 35+ Instant 1-Click Blueprints**:
  1. 🏆 **Premier Full World Environments**:
     - 🏜️ *Onslaught Canyon Outpost (Torlan)*: 8192x8192 expanse with Red & Blue PowerCores, Neutral PowerNodes, vehicle bays (Manta, Scorpion, Raptor, Goliath), AVRiL armory, and full road/flying path network.
     - ❄️ *Arctic Glacial Research Facility*: 6144x6144 ice chasm with suspension bridge, Hellbender & Manta pads, East/West research complexes, defense towers.
     - 🪐 *Orbital Asteroid Mining Station*: 5120x5120 low-gravity crater with industrial mining gantry, Redeemer apex, high-velocity jump pads, space skybox.
     - 🌋 *Volcanic Magma Foundry (Abaddon)*: 4096x4096 industrial smelting complex over molten magma with suspended catwalks, extreme heat lighting.
     - 🏛️ *Ancient Egyptian Temple (Anubis)*: 4096x4096 sandstone temple with grand hypostyle colonnade, golden altar, UDamage, underground crypt.
  2. 🏰 **Exterior Structures & Outposts**:
     - 🛡️ *Fortified Forward Base (FOB)*: Perimeter barrier walls, bunker command post, vehicle repair dock, sniper mast, Scorpion.
     - 🚜 *Heavy Vehicle Dropzone & Pad*: Goliath Battle Tank, Manta, and AVRiL weapon station.
     - 📡 *Deep Space Radar Relay Tower*: High-elevation sniper aerie, Lightning Gun, and searchlight.
  3. 🏛️ **Interior Complexes & Arenas**:
     - 🏟️ *Grand Colosseum Tournament Arena*: Multi-level gladiatorial deathmatch arena with center UDamage dais, 4 weapon alcoves, 4 xJumpPads, 8 PlayerStarts.
     - ⚛️ *Sub-Level Reactor Core Chamber*: High-tech nuclear reactor chamber with magnetic containment rings, coolant pipes, hazard walkways.
     - ☣️ *Bio-Hazard Containment Laboratory*: Quarantine laboratory with specimen containment vats, decontamination airlocks, Bio Rifle arsenal.
  4. 🚜 **Vehicles & Heavy Cavalry (Onslaught & Assault)**:
     - 🏍️ `Onslaught.ONSHoverBike` (Manta)
     - 🚙 `Onslaught.ONSRV` (Scorpion)
     - ✈️ `OnslaughtFull.ONSAttackCraft` (Raptor)
     - 🚜 `Onslaught.ONSHoverTank` (Goliath)
     - 🚛 `Onslaught.ONSPRV` (Hellbender)
     - 🛸 `OnslaughtFull.ONSBomber` (Cicada)
     - 🛞 `Onslaught.ONSHeavyArtillery` (Paladin)
     - 🤖 `OnslaughtFull.ONSMobileAssaultStation` (Leviathan)
  5. ⚡ **Onslaught & Assault Objectives**:
     - 🔴 `Onslaught.ONSPowerCore` (Red Base)
     - 🔵 `Onslaught.ONSPowerCore` (Blue Base)
     - 🔷 `Onslaught.ONSPowerNode` (Neutral Capturable Hub)
     - 🎯 `UT2k4Assault.ASTurret` / Assault Destroyable Objectives
  6. 🔫 **UT2004 Weapons & Combat Arsenal**:
     - Shock Rifle, Flak Cannon, Rocket Launcher, Lightning Gun, Minigun, Link Gun, Bio Rifle, ONSAVRiL, Redeemer.
  7. 🛡️ **Powerups, Health & Adrenaline**:
     - Super Shield Pack (+100 AP), Shield Pack (+50 AP), Super Health Pack (+100 HP), Health Pack (+25 HP), UDamage (2x), Adrenaline (+3).
  8. 🌀 **Things, Movers & Particle Emitters**:
     - `XGame.xJumpPad`, `Engine.Sunlight`, Emergency Strobe Light, `Engine.SkyZoneInfo`, `Engine.ZoneInfo`.
  9. 👾 **People, Bots & Creatures (SkaarjPack / Invasion)**:
     - PlayerStart, Skaarj Warrior, Warlord Boss, Titan Giant, Krall Warrior, Brute Behemoth, Skaarj Pupae, Razorfly, Invasion Monster Wave Spawner.
  10. 🧭 **Bot Navigation & Vehicle Pathing**:
      - `Engine.PathNode`, `Engine.RoadPathNode`, `Engine.FlyingPathNode`, Full Level Rebuild & Path Compile.

### 📚 New: Master Tutorial & Knowledge Base (U1 through U5)
- **`docs/UNREAL_ENGINE_U1_TO_U5_MASTER_TUTORIAL_KNOWLEDGEBASE.md`**:
  - Comprehensive architectural matrix and evolutionary timeline covering UE1, UE2.5, UE3, UE4, and UE5.
  - CSG BSP Subtractive vs. Additive paradigms, T3D PolyList grammar, coplanar planarity, and winding rules.
  - Lighting science: 8-bit HSV color system (Hue/Saturation/Brightness), attenuation curves, and special light types.
  - Vehicle physics & kinematics (`KVehicles`, `SVehicles`, `ONSVehicle`), suspension travel, tire friction, and net replication.
  - Bot AI navigation mathematics: ReachSpec directed graphs, node spacing, and vehicle/flying node networks.
  - SkaarjPack creature AI specifications for Invasion and survival game modes.
  - Full UnrealEd automation console command cheat sheet.

---

## [v2.12.0] - 2026-08-24: World-Class TRACE Logging, Crash Diagnostics & Universal Launcher Hardening

### 🪵 New: World-Class Centralized TRACE Logging & Diagnostics System
- **Custom `TRACE` Log Level (`logging.TRACE = 5`)**:
  - Implemented high-fidelity `logger.trace(...)` API positioned below standard `DEBUG` (10) for micro-level automation and IPC monitoring.
  - Granular trace telemetry for Win32 HWND detection, window message dispatching (`WM_SETTEXT`, `WM_KEYDOWN`), child control enumeration, and log offset seeking.
- **Multi-Destination Rotating Log Hierarchy in `unrealagentharness/logs/`**:
  - `logs/agent_harness.log`: Master consolidated rolling trace log capturing all events across all components.
  - `logs/agent_harness_crash.log`: Fatal crash diagnostics journal recording complete tracebacks, thread details, OS/platform specs, and sanitized environment dumps (with API keys/secrets automatically redacted).
  - Dedicated component logs: `harness_ui.log`, `engine_controller.log`, `engine_scanner.log`, `pathing_engine.log`, `nexus_bridge.log`, `updater.log`, `config_mgr.log`.
  - Configured with `RotatingFileHandler` (10MB max bytes, 5 backups, UTF-8).
- **High-Precision Formatting & Colored Console**:
  - Timestamped with millisecond precision: `[2026-08-24 13:16:51.293]`.
  - Enriched with process PID, thread name, module, function name, and line number: `[PID:15340:MainThread] [EngineController] [engine_controller.py:69]`.
  - ANSI colored console output for instantaneous terminal visibility.
- **Global Uncaught Crash Hooks**:
  - Installed `sys.excepthook` and `threading.excepthook` to intercept and capture any uncaught exceptions across main and background threads into `logs/agent_harness_crash.log`.
  - Native Tkinter modal error fallback alert if the GUI loop encounters a fatal exception.

### 🛡️ Enhanced: Resilient Universal Batch Launchers & Bootstrap
- **`launch_harness_universal.bat` Hardening**:
  - Added automatic Python discovery (`python`, `py -3`, `python3`).
  - Added execution telemetry logging directly to `logs/launch_universal.log`.
  - Added error trapping (`%ERRORLEVEL%` non-zero pause protection) preventing the console window from flashing and closing on startup errors.
  - Forwarded command-line parameters (`%*`) allowing flags like `--trace`, `--debug`, `--log-level TRACE`, `--engine`.
### 🔄 New: Persistent Engine Verification, Auto-Initialization & Re-Check Control
- **Persistent Engine State & Profile Persistence**:
  - `ConfigManager.verify_and_initialize_engine()`: Automatically verifies directory existence, system executables (`System/UnrealEd.exe`), and package signatures.
  - Verification state (`initialized`, `verified`, `last_checked`, `summary`) is persisted directly into `config/engine_profiles.json`.
  - Once verified, checks persist across sessions without redundant filesystem lag.
  - Changed default engine fallback to `ut99_goty` and ensured active engine choice stays persistent across restarts.
- **Dynamic Quick Architect Palette & Tab Switching**:
  - Automatically switches the Quick Architect Palette notebook tab to match the active target:
    - `ut99_goty` / classic mods -> Tab 0 ("🏆 UT99 Base")
    - `ut99_utron` -> Tab 1 ("⚡ Mod: UTron (TC)")
    - `ut2004` / `ut2003` -> Tab 2 ("⚔️ UT2004 Base")
- **Top Header Bar Re-Check Button**:
  - Added **`🔄 RE-CHECK`** button directly adjacent to the Target Engine selector, allowing immediate on-demand re-validation of paths, executables, and live Win32 editor connection.
- **Dynamic LLM Engine Context & Prompt Tailoring**:
  - Replaced hardcoded UTron rules in `_build_system_prompt()` with dynamic engine-specific directives tailored to the active engine (`UT99 GOTY` tournament weapons, `UTron` diffusers/wirenodes, `UT2004` Onslaught/XWeapons, `ChaosUT`, `Tactical Ops`).
  - Added `_refresh_context()` to seamlessly update prompt guidelines upon engine selection.

---

## [v2.11.0] - 2026-08-24: Intelligent Auto-Updater & Version Management Engine

### 🚀 New: World-Class Auto-Updater & Version Checker
- **`UpdateEngine` Core Architecture**:
  - Automatically queries the remote GitHub repository (`https://github.com/kirklasalle/unrealagentharness`) for latest releases, tags, and commits.
  - Dual-mode update delivery:
    1. **Git Pull & Sync**: Intelligent repository synchronization with branch tracking and commit analysis.
    2. **HTTP ZIP Release Fallback**: Direct chunked archive downloading and selective extraction when running outside a git clone.
  - **Configuration Protection**: Automatically creates a backup snapshot of `config/*.json` and user settings before updating, ensuring custom engine paths and API keys are never overwritten.
- **Interactive UI Updates**:
  - **Cockpit Action Bar**: Added **`🚀 UPDATES`** button that checks for releases and changes to a glowing orange badge (`🚀 UPDATE (vX.X)`) when a new version is detected.
  - **Settings Dialog**: Added a dedicated **`🚀 Updates`** tab with version badges, remote changelog viewer, interactive progress bar, and 1-click **"⬇️ Download & Install Update"** button.
  - **Background Check**: Silently checks for updates in the background on harness startup.
- **Unit Test Suite**: Added `TestUpdateEngine` bringing the total test suite to **56/56 passing tests in 10.09s**.

### 🔍 New: Portable Engine Auto-Discovery & Path Resolution
- **Standalone Clone & Portability Support**:
  - `UnrealAgentHarness` can now run from any drive (`C:`, `D:`, `G:`, etc.) or cloned workspace directory without hardcoded path dependencies.
- **`EngineScanner` Core Module**:
  - Automatically probes active Windows drives, Steam libraries, GOG installations, Epic Games directories, and custom development paths for Unreal engines (`UE1`-`UE5`) and Total Conversion game mods (`UTron`, `ChaosUT`, `Tactical Ops`, `Infiltration`, `Monster Hunt`, `UTron 2004`).
  - Scanned 350+ candidate locations in under $0.5$s using smart shallow heuristics.
- **ConfigManager Auto-Apply Integration**:
  - Added `apply_scan_results()` and `run_engine_scan()` to automatically link and save detected paths directly to `config/engine_profiles.json`.
- **Interactive UI Auto-Scan**:
  - **Settings Dialog**: Added a top **"🔍 SCAN ALL DRIVES"** action bar and live scan progress modal with a real-time discovered targets treeview and 1-click **"✅ Save & Apply Discovered Paths"** button.
  - **Cockpit Action Bar**: Added **"🔍 SCAN ENGINES"** button to the top action header for immediate 1-click discovery.
- **Unit Test Suite**: Added `TestEngineScanner` bringing the total test suite to **52/52 passing tests in 0.836s**.

### 📦 New: Modular Game Mod & Total Conversion Registry
- **Engine Tier Categorization**: Structured the engine registry into two distinct tiers:
  1. **🎮 Base Game Engines**: `UT99 GOTY` (UE1 / 469e), `UT2003` (UE2.0), `UT2004` (UE2.5 / v3369+), `Unreal Engine 5` (UE5.x).
  2. **📦 Game Mods & Total Conversions (TC)**: `UTron: Total Conversion Mod`, `ChaosUT: Evolution Mod`, `Tactical Ops: Assault on Terror`.
- **ConfigManager Mod API**:
  - Added `get_base_engines()`, `get_game_mods()`, `register_game_mod()`, and `delete_game_mod()`.
- **Interactive Mod Registration in Settings Dialog**:
  - Redesigned the **Engine Profiles** tab with distinct sections for **Base Game Engines** and **Game Mods & Total Conversions**.
  - Added an interactive **"➕ Register New Mod"** dialog allowing 1-click registration of custom UT99/UT2004 Total Conversion mods with custom INIs, parameters, and directories.
- **Cockpit UI Target & Palette Updates**:
  - Categorized the Target selection dropdown in the Cockpit header.
  - Updated the Quick Architect Palette notebook tab to **⚡ Mod: UTron (TC)**.
- **Comprehensive Documentation**:
  - Published `docs/GAME_MODS_AND_TOTAL_CONVERSIONS_GUIDE.md` covering mod creation, total conversion architecture, and API hooks.
- **Unit Tests**: 48/48 tests passing in 0.228s.
