# Changelog - UnrealEd Agent Harness & World Architect Engine

All notable changes, architectural enhancements, and procedural world-building procedures are documented in this file.

---

## [v2.9.0] - 2026-08-24: Dedicated Game Mods & Total Conversion (TC) Architecture

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

### 🏰 Fixed & Enhanced: Valley Fortress Navigation & Circulation
- **Continuous Castle Entrance Corridor**: Added `CastleCorridor.t3d` ($768 \times 384 \times 384$) connecting the interior Great Hall ($X=768 \rightarrow 1280$) seamlessly through the gatehouse portal all the way to the upper drawbridge ($X=-64 \rightarrow 192$).
- **Castle Tower Stairwells**: Subtracted twin access stairwells (`TowerStairwell.t3d`) inside the fortress keep, providing continuous walking access from the Great Hall ($Z=0$) up to the battlements ($Z=+512$) and parapets ($Z=+1024$).
- **West Mountain Ridge Descent Ramps**: Integrated stepped mountain trail ramps (`MountainRidgeRamp.t3d`, $512 \times 512 \times 512$) connecting the elevated West cliff plateau ($Z=0$) down to the valley floor ($Z=-1024$) and lower stone bridge.
- **Unobstructed AI Reachability**: All 6 PlayerStarts now have unobstructed paths connecting the canyon riverbed, castle interior, and mountain lookouts.

### 🌐 Major Expansion: UTron Profile & Asset Palette
- **Deep 123-Screenshot Reference Study & Master Guide**:
  - Authored `docs/UTRON_ARCHITECTURE_AND_LEVEL_DESIGN_GUIDE.md` cataloging visual benchmarks, grid mechanics, and texture standards from `D:\Projects\GameDevelopment\UTron\UTron_Project_images`.
- **4 Premier UTron World & Grid Blueprints**:
  - ⚡ **Master Control Program (MCP) Core**: Monumental digital sanctum with central rotating MCP cylinder, 4 quadrant platforms, Central Scrutiniser, WireNodes, and full armory.
  - 🏍️ **Light Cycle 90° Grid Arena**: $4096 \times 4096$ neon arena with starting grids, cycle morphs, boundary barriers, and cycle spawns.
  - 💥 **Tank Maze & Combat Grid**: $4096 \times 4096$ tactical maze with digital silos, TankGuns, TankMesh spawns, and Recognizer sentries.
  - 🛸 **Sark's Flagship Carrier Hangar**: $4608 \times 4608$ colossal docking bay with overhead gantry pylons, Drivable Recognizers, command bridge, and deadly disc armory.
- **Full UTron Asset Palette Integration**:
  - **Weapons**: Deadly Identity Disc, Standard Identity Disc, Guard Staff, Jai-Lai Launcher, MPLP Laser, EMP Grenade, Tank Gun, Disc Ammo.
  - **Vehicles**: Light Cycle Blue/Red/Yellow, Power Cycle, Recognizer Patrol, Drivable Recognizer, Tank Mesh, Bonus Saucer, Flightator.
  - **Characters & Bots**: Tron, Commander Sark, Kevin Flynn, System Guard, Bit, Gridbug.
  - **Interactive Entities**: Life Tile, Energy Orb, Data Diffuser, Overclocker, Randomiser, WireNode, OmniBlock, Central Scrutiniser.
- **Unit Test Suite**: 45/45 tests passing in 0.289s.
- **Celestial Skybox Engine with Parallax `SkyZoneInfo`**:
  - Implemented isolated skybox chamber (`ValleySkybox.t3d`) at $X=-8192, Y=-8192, Z=+4096$ textured with `ShaneSky.pansky1` and unlit flags (`Flags=4194304`).
  - Added `Engine.SkyZoneInfo` actor at $(-8192, -8192, 4096)$ emitting real-time alpine skybox perspective.
  - Enhanced `_generate_brush_polylist_t3d` and `_write_brush_file` with `ceil_flags=4194432` (`PF_FakeBackdrop | PF_Unlit`) for seamless sky projection across the canyon ceiling.
- **Grounded Multi-Tower Castle Citadel (Grounded at Z=-1024)**:
  - Additive bedrock stone foundation bluff (`CastleBluffBase.t3d`, `1792x1792x1024`) extending all the way from the canyon floor ($Z=-1024$) to ground level ($Z=0$).
  - Castle keep bastion (`CastleKeepBastion.t3d`) rising from $Z=0$ to $+512$.
  - Subtracted Castle Great Hall & Armory interior (`CastleGreatHall.t3d`).
  - Fortified arched gatehouse portal with portcullis (`CastleGatePortal.t3d`).
  - 4 flanking octagonal battle towers (`CastleBattleTower.t3d`, `sides=8`, NW/SW/NE/SE) rising from $Z=0$ to $+1024$ and high royal citadel spire (`CitadelSpire.t3d`) rising to $+1408$.
- **West Mountain Ridge Plateau & 2 Lookout Towers**:
  - Solid mountain ridge shelf (`WestMountainRidge.t3d`, `896x3584x1024`) extending from canyon floor to $Z=0$.
  - 2 octagonal peak lookout watchtowers (`MountainLookout.t3d`, `sides=8`) rising to $+768$ with Sniper Rifles.
- **Dual Bridges Over the Gorge**:
  - Lower masonry stone arch bridge (`LowerStoneBridge.t3d`) with approach ramps spanning the river chasm at $Z=-768$.
  - Upper timber drawbridge (`UpperDrawbridge.t3d`, `512x384x48`) connecting cliff trail to the castle gatehouse.
- **Mountain Cliffs, River Gorge & Waterfalls**:
  - Deep central river gorge (`RiverGorge.t3d`, `1024x4608x256`) with riverbed pebbles and crystal blue water.
  - West mountain waterfall cascade recess (`WaterfallChamber.t3d`, `384x768x1280`) with animated water textures and shimmer lighting (`LE_WateryShimmer`).
- **Living World Foliage, Rocks & Torches**:
  - 16+ 3D pine trees (`Tree1`, `Tree2`, `Tree3`, `Tree6`), mountain shrubs (`Plant1`-`Plant7`), granite boulders (`BigRock`, `Boulder`, `SmallRock`), and medieval wall torches (`TorchFlame`).
- **Botpack AI Reachability**:
  - 32-node reachability network covering the canyon floor, river gorge, stone bridge, drawbridge, castle interior, and sniper lookouts.

---

## [v2.6.0] - 2026-08-23: Deep Unreal Research, Market Landscape & Level Design Knowledge Base

### 📚 Added: Comprehensive Knowledge Base & Technical Guides
- **`docs/WORLD_CLASS_UNREAL_LEVEL_DESIGN_GUIDE.md`**:
  - **UE1 / UT99 / OldUnreal 469e**: Power-of-two grid snapping, solid vs. semisolid brush optimization, non-planar polygon prevention, airtight zone portal sealing, water/low-g zone physics, key/ambient radiosity ratios, dynamic lighting effects (`LE_TorchWaver`, `LE_WateryShimmer`), texture scaling/panning (`SCALE 2.0`), surface flags (`Unlit`, `Two-Sided`, `Masked`, `FakeBackdrop`), and Botpack AI navigation lattices with +50 UU clearance.
  - **UE2.5 / UT2004**: Static mesh architecture, `AntiPortalActor` bounding box occlusion, `CullDistance` optimization, multi-layer shaders (`Engine.Shader`), `FluidSurfaceInfo` interactive water, Onslaught `PowerCore`/`PowerNode` routing, and vehicle navigation networks.
  - **UE5.x**: Nanite virtualized geometry rules, Lumen global illumination software/hardware raytracing, World Partition spatial streaming, Procedural Content Generation (PCG) biome graphs, and Python Remote Execution (Port 30010).

### 📊 Added: Market Landscape & Competitive Analysis
- **`docs/MARKET_LANDSCAPE_AND_COMPETITIVE_ANALYSIS.md`**:
  - Comparative benchmark of **Unreal Agent Harness** vs. **Promethean AI**, **Ultimate Engine Copilot**, **Autonomix**, and **UnrealGPT**.
  - Highlights Unreal Agent Harness's unique industry positioning as the world's **first and only multi-generational (UE1 to UE5)** autonomous level architect providing full-stack CSG synthesis, lighting compilation, and bot reachability graphs with zero UI overhead.

---

## [v2.5.0] - 2026-08-23: Premier Outdoor World Architect & Dynamic Texture Loading

### 🌲 Added: 3 Premier Outdoor World Blueprints
- **🏔️ Verdant Mountain Valley (`generate_ut99_verdant_mountain_valley`)**:
  - **Scale**: 4096 x 4096 x 1536 mountain canyon valley.
  - **CSG Architecture**: Subtractive valley terrain with carved river gorge (`Pebbles`), additive stone fort fortress (`CasWAL` / `oldflor`), subtracted fort interior sanctum and arched entryway (`Casdoor2`), additive stone bridge with dual access ramps (`steps`), and an elevated octagonal watchtower (`npillar` / `ntrim2`).
  - **World Foliage & Props**: Authentic 3D pine trees (`UnrealShare.Tree1`, `Tree2`, `Tree3`, `Tree6`), mountain shrubs and ferns (`Plant1`, `Plant2`, `Plant3`), granite boulders (`UnrealI.BigRock`, `UnrealShare.Boulder`), and fortress wall torches (`TorchFlame`).
  - **Armory & Items**: Shock Rifle, Flak Cannon, Minigun, Eightball Rocket Launcher, Sniper Rifle in watchtower, Redeemer on center bridge, Body Armor in fort, Shield Belt on watchtower perch, Keg of Health under bridge, MedBoxes, and riverside Health Vials.
  - **Atmosphere & Pathing**: Warm sunlight key (`Hue=38`, `Sat=110`) + sky ambient fill (`Hue=155`, `Sat=160`) with a 20-node Botpack AI reachability network.

- **🏜️ Arid Desert Canyon & Excavation Ruins (`generate_ut99_desert_canyon_ruins`)**:
  - **Scale**: 4608 x 4608 x 1792 sun-drenched desert canyon.
  - **CSG Architecture**: Subtractive sandstone canyon (`path` / `Basicrok2`), sand plateau with long stone ramp (`FLOOR2B` / `BRIXG`), ancient sandstone temple with interior sanctum (`HIWALL1B` / `CARVIN1A`), carved doorway, twin colonnade columns (`COLUMN3`), and an oasis well basin (`FLORROK1` / `TRIM2A`).
  - **World Foliage & Props**: Desert cacti and shrubs (`Plant5`, `Plant7`), ancient monk/Nali statues (`MonkStatue`, `NaliStatue`), ceremonial urns and vases (`Urn`, `Vase`), and desert boulders (`BigRock`, `Boulder`).
  - **Armory & Items**: Rocket Launcher on temple roof, Flak Cannon on sand plateau, Sniper Rifle on canyon ridge, Shock Rifle at oasis, Minigun in temple hall, Body Armor, Shield Belt, Jump Boots, Health Pack, and MedBoxes.
  - **Atmosphere & Pathing**: Blazing sun key (`Hue=25`, `Sat=180`) + desert dusk fill (`Hue=225`, `Sat=140`) with 15-node canyon/plateau AI network.

- **🌌 Orbital Asteroid Outpost (`generate_ut99_orbital_asteroid_outpost`)**:
  - **Scale**: 4096 x 4096 x 1536 low-gravity asteroid crater.
  - **CSG Architecture**: Subtractive 16-sided cylindrical crater basin (`rClfFlr1x` / `mlbPipeWall7TES` / `NCld`), additive octagonal center landing pad (`rCFlr12x`), command habitation module with interior living quarters (`bmwall3` / `Mys_pan1` / `bmCeiling3`), airlock portal (`doorC2`), elevated comm relay platform with antenna mast (`rClfPlr4` / `rClfPlr5`), and access ramp.
  - **Physics & Props**: Low gravity field (`ZoneGravity=(Z=-350)`), meteorite fragments (`BigRock`, `Boulder`), cargo containers and barrels (`Barrel`, `Chest`), and beacon lanterns (`Lantern`, `Lantern2`).
  - **Armory & Items**: Sniper Rifle on comm mast, Redeemer on comm dais, Shock Rifle on landing pad, Flak Cannon on crater floor, Minigun at airlock, Shield Belt, Body Armor, Jump Boots, and MedBoxes.
  - **Atmosphere & Pathing**: Deep space starfield lighting (`Hue=155`, `Sat=240`) + cyan comm beacons (`Hue=145`, `Sat=255`) with full low-gravity reachability graph.

---

### 🎨 Fixed: Texture Package Preloading (`OBJ LOAD`)
- **Problem**: When importing `.t3d` PolyLists into UnrealEd 1 (`BRUSH IMPORT`), polygon textures defaulted to blank gray or `DefaultTexture` if the package had not been manually opened in the Texture Browser.
- **Root Cause**: `PolysFactory` in UnrealEd requires package definitions loaded in active memory to bind texture names during `.t3d` parsing.
- **Solution**: Injected `OBJ LOAD FILE="..\Textures\<Package>.utx" PACKAGE=<Package>` immediately following `MAP NEW`. All packages (`GenEarth`, `NaliCast`, `ShaneSky`, `Ancient`, `SkyBox`, `SpaceFX`, `UTtech1`, `UTtech2`) load into the Texture Browser prior to geometry carving.

---

### 🏗️ Saved & Finalized: 2-Stage CSG & Entity Synthesis Pipeline
1. `MAP NEW` -> Resets level hierarchy.
2. `OBJ LOAD FILE="..." PACKAGE=...` -> Loads all requisite `.utx` texture packages.
3. `MAP IMPORT FILE="*Actors.t3d"` -> Places LevelInfo, ZoneInfo, PlayerStarts, Weapons, Pickups, 3D Decor Props, Lights, and PathNodes.
4. `BRUSH MOVETO` + `BRUSH IMPORT` + `BRUSH SUBTRACT/ADD` -> Carves world terrain, rooms, bridges, forts, and towers.
5. `MAP REBUILD` -> Compiles BSP solid node hierarchy.
6. `LIGHT APPLY` -> Computes dynamic raytraced radiosity lighting.
7. `PATHS BUILD` -> Computes AI reachability table and navigation network.
8. `FLUSH` -> Synchronizes all 4 editor viewports.

---

### 🧪 Test Suite & Verification
- **Total Unit Tests**: 42 passed in 0.45s (`AgentHarness/test_harness.py`).
- **Coverage**: ConfigManager, FormulaEngine, ToolsSchema, NexusBridge, EngineController, PathingEngine, and VisionInspector.
