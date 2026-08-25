# Unreal Agent Harness
### Autonomous Level Designer, In-Editor Copilot & Multi-Engine Automation Suite

<p align="center">
  <img src="assets/hero_banner.jpg" alt="Unreal Agent Harness Hero Banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Audit%20Score-96.25%20%2F%20100%20(World--Class)-brightgreen?style=for-the-badge&logo=checkmarx" alt="Audit Score">
  <img src="https://img.shields.io/badge/Standard-UAH%20v1.0.0-gold?style=for-the-badge&logo=openaccess" alt="UAH Standard">
  <img src="https://img.shields.io/badge/Engines-UE1%20%7C%20UE2.0%20%7C%20UE2.5%20%7C%20UE5.x-blue?style=for-the-badge&logo=unrealengine" alt="Supported Engines">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-green?style=for-the-badge&logo=python" alt="Python Support">
  <img src="https://img.shields.io/badge/LLM-Gemini%202.5%20%7C%20Claude%203.7%20%7C%20GPT--4o%20%7C%20Ollama-purple?style=for-the-badge&logo=openai" alt="LLM Providers">
  <img src="https://img.shields.io/badge/Interop-.nexus%20AMTP%20v3.0-orange?style=for-the-badge" alt="Nexus AMTP">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge" alt="License">
</p>

---

## 🌟 Executive Summary

The **Unreal Agent Harness (UAH)** is the official reference implementation of the **[UAH Open Standard (v1.0.0)](docs/UAH_UNREAL_AGENTIC_HARNESS_STANDARD_SPECIFICATION.md)** — a portable, zero-dependency autonomous level design, CSG geometry compilation, bot pathing, multi-modal perception, and multi-agent coordination standard for the Unreal Engine ecosystem (UE1 through UE5).

UAH is officially certified with a **96.25 / 100 World-Class Health Score** in our **[Comprehensive Software Application Audit (v2.14.0)](docs/07_COMPREHENSIVE_SOFTWARE_APPLICATION_AUDIT.md)**, uniting low-level Win32 automation with cutting-edge frontier reasoning models (Google Gemini 2.5 Flash, Anthropic Claude 3.7 Sonnet, OpenAI GPT-4o) and 100% private, air-gapped offline runtimes (Ollama Qwen 2.5 Coder 32B).

For future milestones and development trajectory, explore the **[Official Engineering & Product Roadmap (2026–2027)](ROADMAP.md)**.

<p align="center">
  <img src="assets/architecture_matrix.jpg" alt="System Architecture & Multi-Engine Matrix" width="100%">
</p>

---

## 🚀 Key Architectural Pillars

### 1. ⚡ Zero-Overhead Native Win32 / Tkinter Cockpit
- Built purely on Python and native Win32/Tkinter primitives.
- Operates with **zero Chromium / CEF / WebView2 overhead** (< 35MB RAM footprint), ensuring UnrealEd viewports and real-time BSP compilation never experience framerate stutter or CPU thread starvation.
- Dockable companion window with active LLM chat, real-time command telemetry, quick architect action palettes, and diagnostic logging.

### 2. 🧙 Dual-Mode Unreal Architect Wizard & Mind-to-World Synthesizer
Connects human intuitive intent directly to the live visual interactive viewport:
- **✨ Clean Slate Mode**: Synthesizes complete standalone worlds with deep 1998 *Unreal* single-player RPG lore, `TranslatorEvent` message tablets, `Nali` monks, `Skaarj` AI enemies, and secret subterranean crypts.
- **➕ In-Situ Non-Destructive Extension**: Injects connected rooms, crypts, sniper overlooks, and corridors directly into whatever active map is currently open in UnrealEd without resetting geometry.
- **75% Engine Budget Law**: Mathematically bounds procedural complexity to maximize visual and spatial fidelity without triggering 65k node GPF crashes or BSP cuts.

<p align="center">
  <img src="assets/outdoor_worlds_showcase.jpg" alt="Outdoor World Environments Thematic Concept Art" width="100%"><br>
  <sub>🎨 <em>Thematic Architectural Concept Art & Creative Vision (Target Inspirations for Procedural Level Archetypes)</em></sub>
</p>

#### 🏆 Procedural Blueprint & Narrative Catalog:
* **🧙 Unreal 1 RPG Campaigns (Chizra Temple, Skaarj Mothership, Bluff Eversmoking)**: Grand vaulted naves, fluted sanctuary columns, TranslatorEvent lore tablets, Nali monks, Brute guards, Skaarj assassins, and secret subterranean crypts.
* **🏔️ Verdant Mountain Valley (`4608 x 4608 x 1536`)**: Alpine valley with riverbed gorge, stone fortress with living quarters, stone bridge with dual ramps, octagonal sniper watchtower, 3D pine trees (`Tree1`–`Tree6`), mountain ferns, torches, weapons, and 52-node AI reachability network.
* **🏜️ Arid Desert Canyon & Ruins (`4608 x 4608 x 1792`)**: Sun-drenched sandstone canyon with ancient temple, colonnade columns, sand plateau ramp, oasis basin, desert cacti, monk/Nali statues, ceremonial urns, and full pathing.
* **🌌 Orbital Asteroid Outpost (`4096 x 4096 x 1536`)**: Low-gravity asteroid crater (`ZoneGravity.Z = -350`), pressurized command hab module, airlock entryway, landing pad, comm relay mast, meteorite boulders, cargo containers, beacons, and cosmic starfield.
* **🏟️ Classic Tournament Arena (`3072 x 3072 x 1024`)**: Multi-tier deathmatch arena with central combat dais, semi-solid fluted pillars, perimeter trim moldings, crown cornices, recessed lighting alcoves, jump pad, mezzanine balcony, and authentic thematic textures.
* **🚩 Symmetrical CTF Fortresses (Red & Blue Bases)**: Flag daises, sniper perches, team defense points, and connecting midfield hallways.
* **🕹️ UTron Discs of Tron & Light Cycle Grids**: Neon cylindrical platforms, diffuser bus lines, and wirenode trigger matrices.

<p align="center">
  <img src="assets/unrealed_temple_arena.png" alt="UnrealEd Live Dynamic Lighting and CSG Arena Synthesis" width="32%">
  <img src="assets/unrealed_ctf_red.png" alt="UnrealEd Live Symmetrical Red Base Synthesis" width="32%">
  <img src="assets/unrealed_ctf_blue.png" alt="UnrealEd Live Symmetrical Blue Base Synthesis" width="32%"><br>
  <sub>🖥️ <em>Live In-Editor Procedural CSG Brush Carving, Dynamic Lighting & Botpack AI Navigation Lattice in UnrealEd (Unreal Tournament 99 GOTY / 469e)</em></sub>
</p>

### 3. 🧠 Persistent SQLite Memory & Autonomous Skill Genesis
- **Lifelong Wisdom Store**: Automatically parameterizes novel architectural techniques and records them as persistent `.uah_skill` entries in SQLite memory.
- **Dynamic Knowledge Retrieval (RAG)**: Full-text indexing and semantic search over the entire `docs/` compendium for intelligent runtime prompt augmentation.
- **Build Telemetry Recorder**: Logs build history, engine targets, command counts, and reachability scores.

### 4. 🎨 Dynamic In-Memory Texture Package Loading (`OBJ LOAD`)
- Automatically resolves and preloads stock `.utx` texture packages (`GenEarth.utx`, `NaliCast.utx`, `ShaneSky.utx`, `Ancient.utx`, `SkyBox.utx`, `SpaceFX.utx`, `UTtech1.utx`, `UTtech2.utx`, `Coret_FX.utx`) via `OBJ LOAD FILE="..\Textures\<pkg>.utx" PACKAGE=<pkg>`.
- Guarantees that every imported brush polygon immediately binds to high-resolution textures without falling back to flat gray or `DefaultTexture`.

### 5. 🧠 Multi-Provider LLM Intelligence Matrix
Connects to both cutting-edge cloud models and local offline neural networks (evaluated across our **Top 20 LLM Benchmark Suite**):

| Model | Provider | Recommended Use Case | Speed | Cost Tier |
| :--- | :--- | :--- | :---: | :---: |
| 🥇 **Google Gemini 2.5 Flash** | Google AI Studio | **Top Overall Sweet Spot**: Sub-400ms speed, 1M context, exceptional JSON tool calling, multi-modal viewport vision. | ⚡ Ultra-Fast | 💰 Ultra-Budget |
| 🥈 **Google Gemini 2.5 Pro** | Google AI Studio | **Deep Architecture**: 2M context, unmatched multi-room reasoning, full package code trees. | 🚀 Fast | 💰 Mid-Tier |
| 🥉 **Claude 3.7 Sonnet** | Anthropic | **Hybrid Reasoning**: Extended thinking for complex coordinate math & UnrealScript syntax. | 🚀 Fast | 💎 Flagship |
| **OpenAI GPT-4o** | OpenAI | **Rock-Solid Tool Calling**: Consistent schema execution and standard in-editor commands. | 🚀 Fast | 💎 Flagship |
| **Qwen 2.5 Coder 32B** | Local (Ollama) | **Top Offline Model**: 100% private, zero internet required, exceptional code/T3D syntax. | 💻 Local GPU | 🆓 Free / Offline |

*Explore the full evaluated ranking in the **[Top 20 LLM Setup & Evaluation Guide](docs/LLM_PROVIDER_SETUP.md)**.*

### 6. 🌐 .nexus AMTP v3.0 Protocol & Chirpy Interoperability
- Seamlessly bridges telemetry and level blueprints to Kirk LaSalle's **.nexus Agent Post Office** (`d:\projects\.nexus`) using Agent Mail Transfer Protocol (**AMTP/3.0**).
- Dispatches autonomous micro-broadcasts to the Chirpy network (`chirpyagent.com`) with level metrics, compilation summaries, and reachability reports.

---

## 🎮 Supported Engine Matrix

| Profile ID | Target Engine & Version | Default System Directory | Target Executable | Primary Features |
| :--- | :--- | :--- | :--- | :--- |
| `ut99_goty` | Unreal Tournament 99 GOTY (UE1 / 469e) | `G:\UnrealTournament\System` | `UnrealEd.exe` | Botpack weapons, ZoneInfo, 3D foliage, radiosity lighting, AI paths |
| `ut99_utron` | UTron Total Conversion (UE1) | `G:\UnrealTournament\System` | `UnrealEd.exe` | Identity Discs, diffusers, wirenodes, light cycle grids |
| `ut99_chaosut` | ChaosUT: Evolution Mod (UE1) | `G:\UnrealTournament\System` | `UnrealEd.exe` | Crossbow, Proxy mines, Vortex cannons, Gravity belts, Turrets |
| `ut99_tacticalops` | Tactical Ops: Assault on Terror (UE1) | `G:\UnrealTournament\System` | `UnrealEd.exe` | Buy zones, Hostage rescue points, Terrorist/Special Forces spawns |
| `ut2003` | Unreal Tournament 2003 (UE2.0) | `G:\UT2003\System` | `UnrealEd.exe` | Early static mesh brushes, xWeapons, terrain actors |
| `ut2004` | Unreal Tournament 2004 (UE2.5) | `G:\UnrealTournament2004\System` | `UnrealEd.exe` | Onslaught PowerNodes, Karma physics, vehicle bays, Assault turrets |
| `ue5` | Unreal Engine 5.x (Modern UE) | `<ProjectRoot>` | `UnrealEditor.exe` | Python Remote Execution (Port 30010), Nanite, Lumen |

---

## 🛠️ Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested up to Python 3.14 on Windows 10 / 11)
- Unreal Tournament 99 (v436 or OldUnreal 469e) / Unreal Tournament 2004 (v3369+)

### Installation
Clone the repository into your Unreal Tournament root or preferred tools directory:

```bash
git clone https://github.com/kirklasalle/unrealagentharness.git AgentHarness
cd AgentHarness
pip install -r requirements.txt
```

### Launching the Cockpit

Launch with the dedicated batch script for your target game:

```cmd
:: Universal Selector (Choose engine profile on launch)
launch_harness_universal.bat

:: Unreal Tournament 99 GOTY
launch_harness_ut99_goty.bat

:: UTron Total Conversion Mod
launch_harness_ut99_utron.bat

:: Unreal Tournament 2004
launch_harness_ut2004.bat
```

---

## 🏗️ The 2-Stage CSG & Entity Synthesis Pipeline

To prevent brush clipping, level wipeouts, and missing polygon textures, the Harness executes level construction in a synchronized 2-stage pipeline:

```mermaid
graph TD
    A[MAP NEW] --> B[OBJ LOAD Texture Packages]
    B --> C[MAP IMPORT Actors & Entities]
    C --> D[BRUSH MOVETO & BRUSH IMPORT Geometry]
    D --> E[BRUSH SUBTRACT / ADD CSG Carving]
    E --> F[MAP REBUILD BSP Solid Hierarchy]
    F --> G[LIGHT APPLY Raytraced Radiosity]
    G --> H[PATHS BUILD Botpack AI Graph]
    H --> I[FLUSH 3D Viewports]
```

1. **`MAP NEW`**: Clean slate level initialization.
2. **`OBJ LOAD`**: Preloads `.utx` texture packages into UnrealEd memory.
3. **`MAP IMPORT`**: Places `LevelInfo`, `ZoneInfo`, `PlayerStarts` (+50 UU floor clearance), weapons, pickups, 3D trees/rocks/torches, and `PathNodes`.
4. **`BRUSH SUBTRACT / ADD`**: Carves terrain, valleys, rooms, bridges, and towers around entities.
5. **`MAP REBUILD`**: Compiles BSP solid node tree.
6. **`LIGHT APPLY`**: Traces dynamic color and radiosity lighting.
7. **`PATHS BUILD`**: Generates AI reachability table and navigation lattice.
8. **`FLUSH`**: Updates and renders all 4 editor viewports.

---

## 📁 Repository Structure

```
AgentHarness/
├── assets/                          # Illustrations, hero banners & in-editor screenshots
├── config/                          # Dynamic engine, LLM provider & persona profiles
│   ├── engine_profiles.json
│   ├── llm_profiles.json
│   └── personality_profiles.json
├── core/                            # Core engine logic and IPC bridges
│   ├── config_manager.py            # Profile and configuration loader
│   ├── engine_controller.py         # Win32 window discovery and command injection
│   ├── formula_engine.py            # Procedural level formulas and CSG synthesizers
│   ├── memory_engine.py             # Persistent SQLite memory, RAG indexer & wisdom store
│   ├── mind_synthesizer.py          # SOTA Mind-to-World neuro-symbolic level architect
│   ├── skill_genesis.py             # Lifelong autonomous skill formalizer
│   ├── wizard_builder.py            # Dual-mode Unreal Architect Wizard builder
│   ├── llm_engine.py                # Multi-provider LLM driver with native tool calling
│   ├── logger.py                    # Unified file and console logging
│   ├── nexus_bridge.py              # AMTP/3.0 Post Office & Chirpy network bridge
│   ├── pathing_engine.py            # Botpack AI reachability and lattice generator
│   ├── vision_inspector.py          # Viewport screen capture and analysis
│   └── tools_schema.py              # Function calling schemas for LLMs
├── ui/                              # Native Win32 UI Cockpit
│   ├── tk_harness_cockpit.py        # Dockable agent cockpit
│   ├── wizard_builder_dialog.py     # Interactive multi-step Architect Wizard UI
│   ├── palette_ut99_goty.py         # UT99 GOTY quick action palette
│   ├── palette_ut99_utron.py        # UTron TC quick action palette
│   ├── palette_ut2004.py            # UT2004 quick action palette
│   └── settings_dialog.py           # Provider setup and diagnostics dialog
├── server/                          # REST & WebSocket Automation Server
│   └── api_server.py                # FastAPI server (Port 9090)
├── docs/                            # 25+ Master guides, architectural audits & specifications
│   ├── 00_MASTER_DOCUMENTATION_INDEX_AND_SYSTEM_MAP.md
│   ├── UNREAL_ARCHITECT_WIZARD_GUIDE.md
│   ├── UAH_MIND_TO_WORLD_SOTA_SPECIFICATION.md
│   ├── 07_COMPREHENSIVE_SOFTWARE_APPLICATION_AUDIT.md
│   ├── LLM_PROVIDER_SETUP.md
│   ├── ROADMAP.md
│   ├── MARKET_LANDSCAPE_AND_COMPETITIVE_ANALYSIS.md
│   ├── UAH_UNREAL_AGENTIC_HARNESS_STANDARD_SPECIFICATION.md
│   ├── UNREAL_ENGINE_U1_TO_U5_MASTER_TUTORIAL_KNOWLEDGEBASE.md
│   └── ARCHITECTURE.md ...
├── tools/                           # UnrealScript compilation & extraction tools
│   ├── Compile-UnrealScript.ps1     # Automated UCC make compiler with backups
│   ├── Extract-UnrealScript.ps1     # Automated UCC batchexport script extractor
│   ├── Extract_All_Scripts.bat
│   └── Build_UTron.bat
├── logs/                            # Diagnostic runtime traces
├── LICENSE                          # Official MIT License (Kirk LaSalle 2026)
├── ROADMAP.md                       # Official 2026-2027 Engineering & Product Roadmap
├── CHANGELOG.md                     # Full release and architectural changelog
├── requirements.txt                 # Python dependencies
├── test_harness.py                  # Automated 103-test verification suite
└── launch_harness_*.bat             # Standalone Windows launchers
```

---

## 📖 Comprehensive Documentation Library

For in-depth technical documentation, refer to the **[Master Documentation Index](docs/00_MASTER_DOCUMENTATION_INDEX_AND_SYSTEM_MAP.md)**:

* **[Unreal Architect Wizard Builder Guide](docs/UNREAL_ARCHITECT_WIZARD_GUIDE.md)**
* **[Mind-to-World SOTA Specification (75% Budget Law)](docs/UAH_MIND_TO_WORLD_SOTA_SPECIFICATION.md)**
* **[Top 20 LLM Setup & Evaluation Guide](docs/LLM_PROVIDER_SETUP.md)**
* **[Comprehensive Software Application Audit & Critical Review](docs/07_COMPREHENSIVE_SOFTWARE_APPLICATION_AUDIT.md)**
* **[Official Engineering & Product Roadmap (2026–2027)](ROADMAP.md)**
* **[Market Landscape & Competitive Intelligence Audit](docs/MARKET_LANDSCAPE_AND_COMPETITIVE_ANALYSIS.md)**
* **[UAH Standard Specification (v1.0.0)](docs/UAH_UNREAL_AGENTIC_HARNESS_STANDARD_SPECIFICATION.md)**
* **[Unreal Engine U1 to U5 Master Tutorial Knowledgebase](docs/UNREAL_ENGINE_U1_TO_U5_MASTER_TUTORIAL_KNOWLEDGEBASE.md)**
* **[System Architecture & Telemetry Specification](docs/ARCHITECTURE.md)**
* **[World-Class Unreal Level Design Guide](docs/WORLD_CLASS_UNREAL_LEVEL_DESIGN_GUIDE.md)**
* **[UnrealEd Skybox & Exterior World Guide](docs/UNREALED_SKYBOX_AND_EXTERIOR_WORLD_GUIDE.md)**
* **[UnrealScript Language Reference & Syntax](docs/02_UNREALSCRIPT_LANGUAGE_REFERENCE.md)**
* **[Package Extraction & Compilation Guide](docs/03_EXTRACTION_AND_COMPILATION_GUIDE.md)**
* **[UTron Project Audit & Modding Manual](docs/04_UTRON_PROJECT_AUDIT_AND_DEV_GUIDE.md)**
* **[UTron UT2004 Porting & Compatibility Guide](docs/06_UTRON_UT2004_PORTING_AND_COMPATIBILITY_GUIDE.md)**
* **[UnrealEd Command Reference](docs/UNREALED_COMMAND_REFERENCE.md)**

---

## 🧪 Testing & Verification

The repository includes a comprehensive 103-test unit testing suite validating configuration profiles, formula generators, tool-calling schemas, IPC controllers, pathing lattice algorithms, Mind-to-World synthesis, Skill Genesis memory persistence, Unreal Architect Wizard building, and .nexus AMTP bridge connections.

To run the full test suite:

```bash
python test_harness.py
```

```
----------------------------------------------------------------------
Ran 103 tests in 6.299s

OK (100% Pass Rate)
```

---

## 🖼️ Visual Assets & Illustration Integrity Manifesto

To maintain complete transparency and technical accuracy, all visual assets in this repository are categorized into two explicit tiers:

### 1. 🖥️ Live In-Editor Viewport Captures (100% Authentic Procedural Output)
These images represent real-time, in-situ captures directly from the active UnrealEd 2.0 / 3.0 viewports executing UAH procedural formulas without post-processing:
* **`assets/unrealed_temple_arena.png`**: Authentic 3072x3072 Nali Temple deathmatch arena with subtractive hull, semi-solid fluted columns, alcove torchlight, and Botpack path lattice.
* **`assets/unrealed_ctf_red.png`**: Authentic Red Base CTF Outpost with flag dais, sniper balcony, weapon spawns, and team defense path nodes.
* **`assets/unrealed_ctf_blue.png`**: Authentic Blue Base CTF Outpost demonstrating symmetrical layout synthesis and dynamic blue key/accent lighting.

### 2. 🎨 Thematic Concept Art & Architectural Vision (Target Inspirations)
These illustrations serve as high-level artistic targets, mood boards, and aesthetic benchmarks that guide the procedural geometry and lighting algorithms:
* **`assets/hero_banner.jpg`**: Brand concept illustrating the neuro-symbolic bridge between human creative intuition and Unreal 3D world space.
* **`assets/architecture_matrix.jpg`**: High-level multi-engine interoperability and IPC communication topology diagram.
* **`assets/outdoor_worlds_showcase.jpg`**: Target aesthetic inspirations for procedural mountain valley, desert ruins, and asteroid outpost archetypes.

---

## 📜 License

Distributed under the **MIT License**. Created by **Kirk LaSalle** for the Unreal Engine and Unreal Tournament community.

