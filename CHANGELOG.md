# Changelog - UnrealEd Agent Harness & World Architect Engine

All notable changes, architectural enhancements, and procedural world-building procedures are documented in this file.

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
