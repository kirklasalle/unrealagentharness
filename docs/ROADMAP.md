# Unreal Agent Harness (UAH) — Official Engineering & Product Roadmap (2026 – 2027)

**Author:** Kirk LaSalle & Antigravity AI Architect  
**Version:** v2.16.2  
**Status:** Active & Executing  
**Target Runtimes:** Unreal Tournament 99 GOTY (UE1), Unreal 1 (UE1), UTron Total Conversion (UE1), ChaosUT, Tactical Ops, UT2003 (UE2), UT2004 (UE2.5), Unreal Engine 5.x  

---

## 🧭 Executive Vision & Mission

The **Unreal Agent Harness** is dedicated to pioneering **autonomous, multi-generational level architecture and game engine intelligence**. By uniting 25+ years of Unreal Engine procedural geometry, Win32 direct-injection automation, AI bot navigation physics, and frontier multi-modal reasoning models (Google Gemini 2.5, Anthropic Claude 3.7, OpenAI GPT-4o, and local air-gapped runtimes), UAH transforms human concept prompts into fully lit, textured, and playable 3D tournament levels in seconds.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        2026 - 2027 ROADMAP TRAJECTORY OVERVIEW                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Q3 2026 (v2.14 - v2.16) │ Multi-Engine Exhaustive Palettes & Ultra Geometry Detail     │
│ Q4 2026 (v2.16 - v2.17) │ Multi-Modal Vision & Direct Viewport Semantic Spatial Engine │
│ Q1 2027 (v3.0 - v3.1)   │ Autonomous Level Synthesis Swarm & .nexus AMTP v3.0 Hub      │
│ Q2 2027 (v3.2 - v3.3)   │ Headless CI/CD Level Testing, Bot Simulation & QA Regression │
│ Q3-Q4 2027 (v4.0)       │ Cross-Engine Universal Level Transpiler (UE1 <-> UE2.5 <-> UE5)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📅 Phased Milestone Matrix

### 🚀 Phase 1: Engine Hardening, Logging & Full Multi-Engine Palettes (Q3 2026 — *Completed*)
*Status: 🟢 Complete & Verified (v2.12.0 – v2.14.0)*

- [x] **Universal Multi-Engine Support**: Full profile switching and live Win32 targeting across `ut99_goty`, `ut99_utron`, `ut99_chaosut`, `ut99_tacticalops`, `ut2003`, and `ut2004`.
- [x] **Centralized TRACE Logging & Diagnostics**: Custom `TRACE` level (5), rotating loggers (`logs/agent_harness.log`), and global crash reporting (`logs/agent_harness_crash.log`).
- [x] **Exhaustive Quick Architect Palettes**:
  - UT99 Base Palette (Deathmatch, CTF, Domination arenas).
  - UTron Total Conversion Palette (Disc Arenas, LightCycle Grids, Diffuser Busses).
  - UT2004 Exhaustive Palette (Onslaught Canyon Torlan, Arctic Glacial, Asteroid Mining, Volcanic Foundry, Egyptian Temple, 8+ heavy vehicles, Skaarj Invasion spawner).
- [x] **Comprehensive Software Application & Critical Audit**: Full audit documentation (`docs/07_COMPREHENSIVE_SOFTWARE_APPLICATION_AUDIT.md`), health scorecards, and model benchmark matrix.
- [x] **Master Tutorial Knowledgebase (U1 to U5)**: 10,000+ word deep architectural guide covering CSG math, T3D poly grammar, HSV lighting science, and bot ReachSpecs.

### 🏛️ Phase 1.5: Ultra Geometry Detail Engine & Unreal 1 Single-Player RPG Mechanics (v2.16.0 – v2.16.2 — *Completed*)
*Status: 🟢 Complete & Verified (v2.16.0 – v2.16.2)*

- [x] **Ultra Geometry Detail Engine (75% Engine Limit Architecture)**:
  - Pushes procedural architecture to 75% of UnrealEd editor limits without causing BSP node overflows or compilation degradation.
  - Parametric PolyList primitives: `BeveledBox`, `Arch`, `Buttress`, `TrimStrip`/`Molding`, `HexColumn`.
  - Semi-solid CSG decoration (`Flags=32` / `PF_Semisolid`) for fluted columns, crown cornices, and baseboards with 0 BSP cuts.
- [x] **Unreal 1 Single-Player RPG Narrative Systems (`generate_unreal1_sp_sanctuary`)**:
  - Narrative lore stone tablets (`TranslatorEvent`), living world NPCs (`Nali` monks, `Brute` guards, `SkaarjWarrior`), and exploration pickups (`DispersionPistol`, `AutoMag`, `NaliFruit`).
- [x] **UT2004 `USkeletalMeshInstance` Crash Resolution & Safe Vehicle Factory Architecture**:
  - Resolved UnrealEd 3 viewport GPF by replacing direct vehicle pawn placement with standard `ONSVehicleFactory` subclasses (`ONSTankFactory`, `ONSHoverCraftFactory`, `ONSRVFactory`, `ONSAttackCraftFactory`, `ONSPRVFactory`, `ONSBomberFactory`, `ONSShockTankFactory`, `ONSMASFactory`).
  - Replaced abstract `ONSPowerNode` with concrete `ONSPowerNodeNeutral`.
  - Added automatic texture package preloader (`_get_ut2004_obj_load_commands`) for all UT2004 world formulas.

---

### 👁️ Phase 2: Multi-Modal Vision & Real-Time Viewport Spatial Perception (Q4 2026)
*Status: 🟡 In Progress / Scheduled (v2.17.0 – v2.18.0)*

- [ ] **High-Fidelity 4K Viewport Inspection**:
  - Implement Win32 DPI-aware screen capture (`SetProcessDpiAwareness`) for pristine multi-monitor 4K coordinate mapping.
  - Multi-viewport capture (Top XY, Front XZ, Side YZ wireframe + 3D Textured perspective) combined into unified multi-modal vision prompts for Gemini 2.5 Pro/Flash and Claude 3.7.
- [ ] **Automated Visual BSP Hole & HOM Glitch Detector**:
  - AI vision agent analyzes rendered viewports after `MAP REBUILD` to visually detect unclosed polygons, Hall-of-Mirrors rendering bugs, or misaligned ceiling textures.
  - Automatically issues corrective vertex adjustments and re-carves geometry.
- [ ] **Lighting & Shadow Contrast Analyzer**:
  - Evaluates ambient vs. key light contrast ratios to ensure competitive visual clarity for tournament deathmatch and CTF sightlines.
- [ ] **Interactive Visual Bounding Box Placement**:
  - Click-and-drag bounding box prompts in the Tkinter Cockpit mapped directly to 3D world coordinates in UnrealEd.

---

### 🐝 Phase 3: Swarm Architecture & Multi-Agent Collaborative Design (Q1 2027)
*Status: ⚪ Scheduled (v3.0.0 – v3.1.0)*

- [ ] **Specialized Agent Swarm Roles over `.nexus` AMTP v3.0**:
  - 🏗️ **Master Architect Agent**: Designs high-level level flow, structural themes, and room topology.
  - 🎨 **Aesthetic & Lighting Agent**: Solves color harmony, HSV values, accent strobe lights, and texture alignment.
  - 🧭 **Navigation & Balance Agent**: Places PathNodes, JumpPads, and weapons; analyzes sightlines, choke points, and powerup timing.
  - 👾 **Encounter & Objective Agent**: Places Invasion monster wave spawners, CTF flag bases, and Assault objectives.
- [ ] **Real-Time Swarm Micro-Broadcasts**:
  - Chirpy network integration broadcasting live milestone telemetry as agents build rooms in parallel.
- [ ] **Multi-User Collaborative In-Editor Sessions**:
  - Web frontend and Tkinter cockpits supporting multi-operator concurrent level drafting with conflict resolution.

---

### 🧪 Phase 4: Headless CI/CD Level Synthesis & Automated Bot QA Testing (Q2 2027)
*Status: ⚪ Scheduled (v3.2.0 – v3.3.0)*

- [ ] **Headless Map Compiler & Validator Pipeline**:
  - CLI tool (`uah-build --preset onslaught_canyon --output ONS-Torlan-AI.ut2`) to procedurally synthesize and compile maps completely headlessly via `UCC.exe make` and script injection.
- [ ] **Automated 16-Bot Simulation & Heatmap Logging**:
  - Automated launching of Unreal Tournament in headless dedicated server mode with 16 AI bots.
  - Generates death heatmaps, weapon pickup frequency charts, and navigation bottleneck reports.
  - AI agent reads simulation logs and autonomously repositions underutilized weapons or widens bottleneck corridors.
- [ ] **GitHub Actions Automated Level Generation**:
  - Automated CI/CD workflows generating fresh daily community challenge maps and compiling `.ut2` / `.unr` distribution packages.

---

### 🌐 Phase 5: Cross-Engine Universal Level Transpiler (Q3 – Q4 2027)
*Status: ⚪ Conceptual & Architectural Design (v4.0.0)*

- [ ] **Bidirectional Level Transpiler (`UAH-Transpile`)**:
  - Transpiles legacy `.unr` (UE1) and `.ut2` (UE2/2.5) maps directly into modern `.umap` assets for **Unreal Engine 5.x** with automated Nanite mesh conversion and Lumen lighting setups.
  - Reverse transpiler converting simple UE5 modular box levels back into legacy CSG brushes for retro tournament play.
- [ ] **Universal Asset Converter**:
  - Automated extraction and modern PBR shader synthesis from legacy `.utx` texture packages.

---

## 🛠️ Technical Debt, Security & Infrastructure Backlog

| Area | Item | Priority | Target |
| :--- | :--- | :---: | :---: |
| **Infrastructure** | Add Win32 DPI awareness calls in `bootstrap.py` for multi-monitor 4K setups. | P1 | v2.15.0 |
| **Reliability** | Wrap HTTP responses in `update_engine.py` to eliminate 404 `ResourceWarning`. | P1 | v2.15.0 |
| **Security** | Add rate limiting and optional JWT bearer authentication to FastAPI bridge. | P2 | v2.16.0 |
| **Documentation** | Expand video and interactive tutorial assets in `docs/reference/`. | P2 | v2.16.0 |
| **Testing** | Expand unit test suite to 100+ tests including simulated Win32 message mocks. | P2 | v2.17.0 |

---

## 📈 Success Metrics & Key Performance Indicators (KPIs)

1. **Synthesis Speed**: Complete tournament-ready 5-room deathmatch arena generated, lit, path-compiled, and ready to play in **< 15 seconds**.
2. **Bot Navigation Quality**: **100% reachability** across all spawned PlayerStarts, weapons, and pickups with zero isolated nodes.
3. **BSP Stability**: **0 BSP holes or HOM errors** across all generated standard blueprints.
4. **Model Compatibility**: 100% feature parity across both frontier cloud LLMs (Gemini 2.5 Flash/Pro, Claude 3.7) and local air-gapped LLMs (Ollama Qwen 2.5 Coder 32B).
