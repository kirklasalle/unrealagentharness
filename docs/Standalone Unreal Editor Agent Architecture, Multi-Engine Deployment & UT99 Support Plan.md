# Standalone Unreal Editor Agent Architecture, Multi-Engine Deployment & UT99 Support Plan

## Goal Description
Transform the **Unreal Editor Agent** into a standalone, portable development package that can be deployed across multiple engine generations:
- **Unreal Tournament 99 GOTY (UE1 / OldUnreal 469e)** & **UTron Total Conversion**
- **Unreal Tournament 2003 (UE2.0)**
- **Unreal Tournament 2004 (UE2.5)**
- **Unreal Engine 5 (UE5 - Planned)**

This plan details copying and synchronizing the full standalone agent suite into `G:\UnrealTournament`, updating and appending all documentation (`README.md`, `PRD.md`, `CHANGELOG.md`, `ROADMAP.md`, and technical guides), and sending an official agent email via the `.nexus` Post Office (`d:\projects\.nexus`) to notify the `Antigravity+gemini@unrealtournament` project agent.

---

## Proposed Changes

### 1. Standalone Universal Agent Harness Architecture Enhancements

#### [MODIFY] [config/engine_profiles.json](file:///g:/UnrealTournament2004/AgentHarness/config/engine_profiles.json)
- Add complete engine definitions for:
  - `ut99_goty`: Native OldUnreal 469e / UE1, Botpack signature weapons (`ShockRifle`, `UT_Eightball`, `UT_FlakCannon`, `minigun2`, `SniperRifle`, `UT_BioRifle`, `Enforcer`, `PulseGun`), armor, pick-ups, and CTF/DM game types.
  - `ut99_utron`: UTron Total Conversion (Identity Discs, Diffuser grids, Wirenodes, Light Cycles, Recognizers, Tanks).
  - `ut2003`: UE2.0 static mesh and deathmatch signatures (`xWeapons`, `xPickups`, `xDeathMatch`).
  - `ut2004`: UE2.5 Onslaught vehicles, Karma physics nodes, and full CTF/Onslaught layouts.
  - `ue5`: Planned Unreal Engine 5 profile (Python Remote Execution Port 30010, WebSocket Bridge, Nanite/Lumen, Niagara, Blueprint Actor Spawners).

#### [NEW] [ui/palette_ut99_goty.py](file:///g:/UnrealTournament2004/AgentHarness/ui/palette_ut99_goty.py)
- Interactive palette for classic UT99 GOTY level creation:
  - **Tournament Armory**: Shock Rifle, Flak Cannon, Rocket Launcher, Minigun, Sniper Rifle, Bio Rifle, Enforcer, Pulse Gun, Chainsaw, Redeemer.
  - **Powerups & Armor**: Shield Belt, Body Armor, Thigh Pads, Keg of Health, MedBox, Health Vials, UDamage (Damage Amp), Invisibility.
  - **Navigation & Core**: PlayerStart (Botpack), PathNode, InventorySpot, JumpSpot, LiftCenter, LiftExit, ZoneInfo, SkyZoneInfo, WarpZoneInfo.
  - **Arena Blueprints**: Morbias-style arena pit, Sniper Tower, Dual-Base CTF, Shock Combo corridors.

#### [MODIFY] [ui/tk_harness_cockpit.py](file:///g:/UnrealTournament2004/AgentHarness/ui/tk_harness_cockpit.py)
- Incorporate the new `palette_ut99_goty` alongside `palette_ut99_utron` and `palette_ut2004`.
- Dynamic tab switching and profile synchronization based on active engine selection.

#### [MODIFY] [core/formula_engine.py](file:///g:/UnrealTournament2004/AgentHarness/core/formula_engine.py)
- Add procedural formulas for:
  - `generate_ut99_tournament_arena`: Classic multi-level deathmatch arena with high/low tier weapon placement and pathing.
  - `generate_ut99_ctf_base`: Red/Blue symmetrical CTF base with flag bases, defense perimeters, and sniper perches.
  - `generate_ue5_modular_arena`: UE5 modular arena template.

#### [MODIFY] [core/nexus_bridge.py](file:///g:/UnrealTournament2004/AgentHarness/core/nexus_bridge.py)
- Ensure robust flag support (`-Subject` and `-Subj`) and direct integration with `D:\Projects\.nexus\nexus.ps1`.

---

### 2. Standalone Package Synchronization into `G:\UnrealTournament`

#### [COPY / DEPLOY] To `G:\UnrealTournament`
- Copy `AgentHarness/` (full codebase: `config/`, `core/`, `ui/`, `server/`, `logs/`, batch launchers, tests, `requirements.txt`).
- Copy `AgentBridge/` and `AgentChatUI/` for complete compatibility.
- Root launchers:
  - `Launch_Agent_Harness_Universal.bat`
  - `Launch_Agent_Harness_UTron.bat`
  - `Launch_Agent_Harness_UT99_GOTY.bat`
  - `Launch_UnrealEd_Agent.bat`

---

### 3. Comprehensive Documentation & Guides Overhaul

#### [MODIFY / APPEND] [g:/UnrealTournament2004/README.md](file:///g:/UnrealTournament2004/README.md) & [G:/UnrealTournament/README.md](file:///G:/UnrealTournament/README.md)
- Detail the Universal Standalone Engine Architecture.
- Add multi-generation matrix (UT99 GOTY, UTron, UT2003, UT2004, UE5 planned).
- Installation and portability instructions for drop-in copying across Unreal directories.

#### [MODIFY / APPEND] [g:/UnrealTournament2004/PRD.md](file:///g:/UnrealTournament2004/PRD.md) & [G:/UnrealTournament/PRD.md](file:///G:/UnrealTournament/PRD.md)
- Update Product Requirements Document to cover multi-engine standalone deployment, engine profiling, and planned UE5 Python remote execution.

#### [MODIFY / APPEND] [g:/UnrealTournament2004/CHANGELOG.md](file:///g:/UnrealTournament2004/CHANGELOG.md) & [G:/UnrealTournament/CHANGELOG.md](file:///G:/UnrealTournament/CHANGELOG.md)
- Add milestone entry for Standalone Multi-Engine Deployment, UT99 Full Support, and Nexus AMTP/3.0 integration.

#### [MODIFY / APPEND] [g:/UnrealTournament2004/ROADMAP.md](file:///g:/UnrealTournament2004/ROADMAP.md) & [G:/UnrealTournament/ROADMAP.md](file:///G:/UnrealTournament/ROADMAP.md)
- Update roadmap milestones covering UT99 GOTY, UTron, UT2003, UT2004, and UE5 development phases.

#### [NEW / UPDATE] [G:/UnrealTournament/docs/](file:///G:/UnrealTournament/docs/) & [g:/UnrealTournament2004/docs/](file:///g:/UnrealTournament2004/docs/)
- Ensure guides for Standalone Deployment, Multi-Engine Switching, and UT99 Level Design are synchronized.

---

### 4. Nexus Agentic Mail Notification Dispatch

#### Dispatch via `.nexus` (`D:\Projects\.nexus`)
- Execute `nexus.ps1 mail send` with:
  - **To**: `Antigravity+gemini@unrealtournament`
  - **Subject**: `[DEPLOYMENT] Standalone Unreal Editor Agent Suite Installed & UT99 Support Commenced`
  - **Priority**: `HIGH`
  - **Body**: Comprehensive dispatch detailing the standalone architecture, multi-engine profile matrix, UT99 GOTY & UTron procedural toolsets, and immediate next steps.
- Ensure registry registration in `D:\Projects\.nexus\bridge\mail\registry.json` if required.

---

## Verification Plan

### Automated & Local Script Verification
1. Run `python test_harness.py` inside `g:\UnrealTournament2004\AgentHarness` and `G:\UnrealTournament\AgentHarness`.
2. Verify all engine profiles load cleanly (`ut99_utron`, `ut99_goty`, `ut2003`, `ut2004`, `ue5`).
3. Verify formula engine generates valid CSG batches for UT99, UTron, UT2004, and UE5.
4. Verify `.nexus` mail dispatch:
   - Check `D:\Projects\.nexus\bridge\mail\boxes\antigravity+gemini\inbox` (or `gemini+antigravity`) for the generated message envelope.
   - Run `powershell -ExecutionPolicy Bypass -File D:\Projects\.nexus\nexus.ps1 mail check` and `mail list`.

### Manual & Visual Verification
1. Launch the standalone cockpit in dry-run mode to confirm tabbed palettes for UT99 UTron, UT99 GOTY, and UT2004.
2. Confirm file structures in `G:\UnrealTournament` and `g:\UnrealTournament2004`.
