# The UTron Project: Technical Audit, Mod Architecture & Developer Guide

**Project Name:** UTron (Unreal Tournament Total Conversion Mod)  
**Original Development Era:** 1999 – 2003  
**Lead Developer / Creator:** Kirk LaSalle  
**Core Contributors:** Robin / Zedsquared / malaclypse the coder (Tiles & Logic)  
**Location:** `G:\UnrealTournament\docs\04_UTRON_PROJECT_AUDIT_AND_DEV_GUIDE.md`  

---

## 1. Project Overview & Historical Context

The **UTron Project** is an ambitious total conversion mod for *Unreal Tournament (1999 / GOTY Edition)* that translates the iconic aesthetic, lore, and gameplay of Disney's *TRON* into the Unreal Engine.

### Key Innovations Built into UTron:
1. **Identity Disc Weaponry:** Physics-driven ricocheting energy discs with blocking, recall, derez mechanics, and decapatron decapitation logic (`IdentityDisc.uc`, `DiscBlockFX.uc`, `slapback.uc`).
2. **Drivable Light Cycles & Vehicles:** Custom player pawn vehicle morphing, light trail barriers with fatal wall collisions (`LightCycleY.uc`, `LightCycleR.uc`, `LightCycleB.uc`, `cycleMorph.uc`, `TileTrail.uc`, `btrail.uc`).
3. **Recognizers & Drivable Heavy Armor:** Multi-part recognizer pawns with projectile cannons, animated legs, and custom carcasses (`Recognizer.uc`, `RecoDrivable.uc`, `RecoPawn.uc`, `RecoProj.uc`).
4. **Tank Game & Custom Gametypes:** Specialized vehicle arenas (`TankGame.uc`, `TankGun.uc`, `DiscArena.uc`, `DMP.uc`).
5. **Interactive Diffuser Tile Grid System:** Real-time dynamic luminescent floor and wall tiles that propagate energy pulses across map surfaces to expose underlying game logic and trigger interactive doors/elevators.
6. **Complete Audio & Aesthetic Overhaul:** Custom voicepacks (MCP, Bit, Flynn, Sark, Tron, Female AI), original soundtrack modules, vector-grid textures, and custom UMenu interfaces.

---

## 2. Diagnosis & Resolution: The "Entry Point Not Found" Error

### The Issue
When launching `UTronProject.exe`, Windows displayed the following modal error:
> **UTronProject.exe - Entry Point Not Found**  
> *The procedure entry point `?CallDefaultProc@WWindow@@UAEHIIJ@Z` could not be located in the dynamic link library `G:\UnrealTournament\System\UTronProject.exe`.*

### Root Cause Analysis
1. In 1999–2003, `UTronProject.exe` was compiled or copied against the original **Unreal Tournament v436** native binaries (compiled with Microsoft Visual C++ 6.0).
2. The current installation has been patched with the modern **OldUnreal v469** engine maintenance update.
3. The v469 update modernized `Window.dll`, `Core.dll`, and `Engine.dll` with modern MSVC compilers, improved 64-bit/32-bit compatibility, widescreen handling, and updated C++ class virtual tables (vtables).
4. Because `UTronProject.exe` was still the legacy 436 binary, it attempted to resolve the old mangled C++ symbol `WWindow::CallDefaultProc(...)` in `Window.dll`, which has a modified symbol signature in v469.

### The Fix
To run UTron with complete stability and full modern GPU / multi-core / high-resolution support:
1. Launch UTron using the modern OldUnreal engine launcher with custom INI parameters:
   ```cmd
   UnrealTournament.exe UTronIntro.unr INI=UTronProject.ini USERINI=UTronUser.ini
   ```
2. Update `UTronProject.exe` in `System/` to be a copy of the modern `UnrealTournament.exe` (while archiving the legacy executable as `UTronProject_v436.exe.bak`).
3. Update `UTronEditor.exe` to mirror `UnrealEd.exe` (archiving legacy as `UTronEditor_v436.exe.bak`).
4. Use the newly created `Launch_UTron.bat` and `Launch_UTron_Editor.bat` shortcuts.

---

## 3. UTron Package Architecture & Inventory

### 3.1 Script Packages (`.u`)
- **`UTronMedia.u`:** Base media package containing character definitions and custom voice synthesis:
  - `MCPVoice.uc`, `BitVoice.uc`, `FlynnVoice.uc`, `TronVoice.uc`, `SarkVoice.uc`, `UTronFemaleAIVoice.uc`, `UTronAIvoice.uc`, `UTronVoicePack.uc`.
- **`UTron.u`:** Core gameplay package containing all game rules, weapons, vehicles, and actor systems:
  - **Weapons:** `IdentityDisc.uc`, `DiscAmmo.uc`, `DiscBlockFX.uc`, `OmniBlock.uc`, `slapback.uc`, `TankGun.uc`, `MPLPproj.uc`.
  - **Vehicles & Pawns:** `LightCycleY.uc`, `LightCycleR.uc`, `LightCycleB.uc`, `Recognizer.uc`, `RecoDrivable.uc`, `RecoPawn.uc`, `Flynn.uc`, `Tron.uc`, `Sark.uc`, `cycleMorph.uc`.
  - **Gametypes:** `DiscArena.uc`, `TankGame.uc`, `DMP.uc`.
  - **Interactive Diffusers / Grid:** `TileTrail.uc`, `btrail.uc`, `SFtrail.uc`, `jbtrail.uc`, `GridSnap.uc`.
  - **HUD & Radar:** `UTronRADAR_HUD.uc`, `UTronTournamentScoreBoard.uc`, `UTronTeamScoreBoard.uc`.
- **`UTronMenu.u`:** Complete UWindow GUI override:
  - `UTronWindowRootWindow.uc`, `UTronGameMenu.uc`, `UTronOptionsMenu.uc`, `UTronStartGameWindow.uc`, `UTronPreferencesWindow.uc`, `UTronWindowLookAndFeel.uc`.
- **`UTronBrowser.u`:** Dedicated multiplayer server browser for finding UTron community servers:
  - `UTronBrowserMainWindow.uc`, `UTronBrowserServerListWindow.uc`, `UTronBrowserGSpyFact.uc`.

### 3.2 Maps (`.unr`)
Located in `G:\UnrealTournament\UTronProject\Maps`:
- `UTronIntro.unr` — Animated title sequence and main menu map.
- `UTron-Logo-Map.unr` — High-impact visual brand logo sequence.
- `DOT-Discs-Of-UTron-1.unr` — Classic Discs of Tron arcade arena.
- `DOT-DiscsOfUTron2002.unr` — Expanded high-tech Discs of Tron colosseum.
- `DOT-DiscsOfUTron][.unr` — Sequel arena with multi-level energy rings.
- `DOT-Grid1.unr` — Flat neon grid testing arena for light cycle combat.
- `DOT-LightCycleDemo.unr` — Light cycle physics and AI demonstration course.
- `DOT-gridbug.unr` — Infestation survival arena featuring Grid Bugs.
- `DOT-sarkscarrier.unr` — Multi-tiered battleship flight deck arena.
- `UTronEntry.unr` & `UTronIndex.unr` — System utility levels.

### 3.3 Textures (`.utx`)
Located in `G:\UnrealTournament\UTronProject\Textures`:
- `Tron2002.utx`, `TronSkins.utx`, `FlynnSkins.utx`, `SarkSkins.utx`, `GuardSkins.utx`, `UTronPawnSkins.utx`
- `UTron_Deco.utx`, `UTron_Floors-Walls.utx`, `UTron_Grids-Lines.utx`, `UTron_Sky-Terra-fx.utx`, `UTron_SolidColors.utx`
- `UTronHUD.utx`, `UTroncrosses.utx`, `UTrondiscs.utx`, `UTron-Particles.utx`

### 3.4 Audio & Music (`.uax` / `.umx`)
Located in `G:\UnrealTournament\UTronProject\Sounds` & `Music`:
- `Tron.uax`, `UTronAIvoice.uax`, `UTronMedia1.uax`, `UTronVoice.uax`, `UTron_Intro.uax`
- `1-Alive.umx`, `Anthem.umx`

---

## 4. Deep Dive into Core Gameplay Mechanics

### 4.1 The Identity Disc (`IdentityDisc.uc`)
The Identity Disc is UTron's signature weapon:
- **Primary Fire:** Throws the disc forward at high velocity. The disc ricochets off world geometry (walls, floors, ceilings) with angle calculation and returns to the thrower's hand upon reaching max range or hitting a target.
- **Secondary Fire / Alt-Fire:** Activates a defensive energy shield (`OmniBlock.uc` / `DiscBlockFX.uc`) that deflects incoming discs and projectiles.
- **Decapitation ("DecapaTron"):** High-precision throws targeting the head trigger custom decapitation announcements (`DecapaTronMessage.uc`).

### 4.2 Light Cycle Mechanics (`LightCycle*.uc` + `cycleMorph.uc`)
- Transforming into a Light Cycle alters player collision and movement physics to strict 90-degree vector turns.
- While moving, the cycle spawns continuous energy wall collision volumes (`TileTrail.uc`, `btrail.uc`).
- Any player or AI contacting an active light trail is immediately eradicated (`UTronEradicatedDeathMessage.uc`).

### 4.3 Interactive Diffusers (Robin / Zedsquared System)
As documented by Robin in `UTronReadMe.txt`:
- Diffusers glow when touched, shot, or triggered.
- When stimulated, a diffuser passes its charge to adjacent diffusers, creating dynamic pulses of light that travel across walls and floors.
- By assigning an `Event` tag to terminal diffusers, mappers can create interactive level circuits (e.g. shooting a floor node to send an energy pulse that unlocks a door or triggers an elevator).

---

## 5. Modding & Developing UTron in 2026+

1. **Modify Scripts:** Edit files in `G:\UnrealTournament\UTronProject\<PackageName>\Classes\*.uc`.
2. **Compile:** Run `Build_UTron.bat` to recompile `UTronMedia.u`, `UTron.u`, `UTronMenu.u`, and `UTronBrowser.u`.
3. **Map Making:** Launch `Launch_UTron_Editor.bat` to build new Discs of Tron arenas or Light Cycle grids in UnrealEd.
4. **Playtest:** Launch `Launch_UTron.bat` to test changes instantly.
