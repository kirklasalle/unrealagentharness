# UnrealEd 3.0 Agent — Intelligent Pathing, Settings UI & Quick Build System

Kirk, I've done a complete deep-dive into every file in the codebase. Here's my analysis and plan for all three major features you requested.

---

## 1. Root Cause Analysis: Path Node Timeout & Crash

From the console log and screenshot, the crash sequence is clear:

```
[09:20:38] Auto-executing tool: rebuild_level with args: {'lighting': True, 'paths': True}
[09:20:38] rebuild_level: geo=True, light=True, paths=True
...
[09:26:12] Command dispatched via win32_edit_injection in 334209.36ms  ← 5.5 MINUTES!
```

**What happened:** The LLM called `rebuild_level(paths=True)` which sends `PATHS BUILD` to UnrealEd. But `PATHS BUILD` in UEd 3.0 is a **synchronous, blocking** operation that:

1. Iterates every `NavigationPoint` actor in the level
2. Raycasts visibility checks between **every pair** of path nodes (O(n²) complexity)
3. Tries to create intermediate path nodes on its own — **"Creating intermediate paths"** as shown in the Map Check dialog
4. Freezes the entire Win32 message queue during execution (single-threaded editor)

The bridge's `execute_command()` uses `SendMessage()` (synchronous Win32 call) which **blocks the calling thread** until UnrealEd processes the message — meaning the entire bridge is frozen for 5+ minutes while `PATHS BUILD` runs.

> [!WARNING]
> Additionally, the Map Check dialog shows **"PathNode3 in same location as PathNode2"** and **"PathNode0 in same location as PathNode3"** — the LLM placed overlapping path nodes, making the `PATHS BUILD` algorithm attempt infinite intermediate paths between zero-distance nodes.

### Proposed Fix: Multi-Layered Intelligent Pathing System

#### Layer 1: Non-Blocking Async Command Dispatch
Replace `win32gui.SendMessage()` with `win32gui.PostMessage()` for long-running commands (`PATHS BUILD`, `MAP REBUILD`, `LIGHT APPLY`). Add a new async execution mode with polling-based completion detection by monitoring the Editor.log for completion markers.

#### Layer 2: Smart PathNode Validation (Pre-Flight)
Before sending `PATHS BUILD`, validate all path nodes:
- **Minimum Distance Check**: Reject/relocate nodes closer than 64 UU apart
- **Duplicate Detection**: Remove or nudge overlapping nodes
- **Boundary Check**: Ensure nodes are within BSP bounds and above floor
- **Grid Snapping**: Snap nodes to a walkable grid aligned with the room geometry

#### Layer 3: Intelligent PathNode Grid Generator
Instead of relying on the LLM to manually place 4-8 nodes, provide a `generate_path_network` tool that:
1. Takes room dimensions/bounds as input
2. Calculates an optimal grid of path nodes with proper spacing (256-512 UU apart)
3. Places nodes at floor level with correct Z offset
4. Connects to existing `PlayerStart` and pickup locations
5. Skips areas inside additive BSP geometry (pillars, walls)

#### Layer 4: Rebuild Timeout Protection
- Set a configurable timeout (default 30s) for `PATHS BUILD`
- If exceeded, auto-dismiss the Map Check dialog and report partial success
- Monitor `Editor.log` for path build completion or error markers

---

## 2. Settings & Configuration Window

The current UI in [tk_editor_chat.py](file:///g:/UnrealTournament2004/AgentBridge/tk_editor_chat.py) has a basic provider dropdown and Test button, but lacks:
- API Key input field
- Model selection dropdown (populated from provider)
- Save button for persistence
- A proper Settings dialog window

### Proposed Design

A **Settings gear button (⚙)** in the header bar opens a new `Toplevel` dialog window:

```
┌─────────────────────────────────────────────┐
│  ⚙ Agent Settings & Configuration          │
├─────────────────────────────────────────────┤
│                                             │
│  Provider:  [▼ Google Gemini            ]   │
│                                             │
│  API Key:   [••••••••••••••••] [👁 Show]    │
│                                             │
│  Base URL:  [https://generativelanguage...] │
│                                             │
│  ── Model Selection ──────────────────────  │
│  Model:     [▼ gemini-2.5-pro          ]   │
│                                             │
│  ── Advanced ─────────────────────────────  │
│  Temperature: [0.2    ]                     │
│  Max Tokens:  [8192   ]                     │
│  [✓] Enable Tool Calling                   │
│  [✓] Enable Vision Input                   │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │ 🔌 Test  │  │ 📥 Fetch │  │ 💾 Save   │ │
│  │Connection│  │ Models   │  │ & Apply   │ │
│  └──────────┘  └──────────┘  └───────────┘ │
│                                             │
│  Status: ✔ Connected (48ms) — gemini-2.5-pro│
└─────────────────────────────────────────────┘
```

**Workflow:**
1. Select Provider → auto-fills Base URL from known defaults
2. Enter API Key → key is masked with `show=*`
3. Click **Test** → runs 5-step diagnostic, reports pass/fail
4. Click **Fetch Models** → queries `/v1/models` and populates Model dropdown with real models
5. Select Model from dropdown
6. Click **Save & Apply** → persists to `AgentConfig.json` and hot-switches the active profile

**Security:** API keys stored locally in `System/AgentConfig.json` with environment variable fallback (already implemented in [config_manager.py](file:///g:/UnrealTournament2004/AgentBridge/config_manager.py)).

---

## 3. Categorized Quick Build Button Palette

Replace the 3 existing suggestion chips at the bottom of the chat with a rich, categorized, scrollable **Quick Build Palette**. The palette uses a tabbed notebook or collapsible accordion with categories.

### Category Design (Curated for UT2004's Asset Library)

| Category | Icon | Buttons |
|:---|:---|:---|
| **🌍 World Environments** | 🌍 | Desert Arena, Forest Clearing, Mountain Fortress, Winter Outpost, Ice Cavern, Volcanic Rift, Urban Street, Space Station |
| **🪨 Terrain & Nature** | 🪨 | Rock Formation, Tree Cluster, Bush Line, Lake/Pond, Waterfall, Cave Entrance, Cliff Wall, Bridge |
| **🏗️ Architecture** | 🏗️ | Concrete Building, Metal Warehouse, Watchtower, Bunker, Corridor, Ramp/Stairs, Doorway, Platform |
| **🤖 Characters & Bots** | 🤖 | Bot Spawn Point, Bot Patrol Path, Sniper Perch, Defender Post, Vehicle Spawn |
| **⚔️ Weapons** | ⚔️ | Shock Rifle, Rocket Launcher, Flak Cannon, Lightning Gun, Minigun, Bio Rifle, Link Gun, Sniper Rifle, Redeemer |
| **💊 Pickups & Powerups** | 💊 | Health Vial, Health Pack, Big Keg O' Health, Shield Pack, Super Shield, Adrenaline, Double Damage, UDamage |
| **🎮 Game Logic** | 🎮 | Player Start, CTF Flag Base, Domination Point, Teleporter Pair, Jump Pad, Trigger/Volume |
| **🔧 Utilities** | 🔧 | 4 Overhead Lights, Path Node Grid, Full Map Rebuild, Playtest Match, Screenshot Viewport, Map Error Check |

### Implementation Approach

Each button sends a carefully engineered natural-language prompt to the AI agent (same as current chips), but with detailed spatial context. For example:

- **"Desert Arena"** → *"Build a large 4096x4096 outdoor desert arena with sandy terrain textures, scattered rock formations, a central elevated platform, overhead sun lighting, weapon pickups, and a full PathNode navigation grid."*
- **"Shock Rifle"** → *"Place a Shock Rifle pickup (XWeapons.ShockRiflePickup) at a strategic position in the current room, slightly above the floor, with good line-of-sight coverage."*

This approach is **superior to hardcoding commands** because:
1. The AI contextualizes placement relative to existing geometry
2. It adapts to the current room's size and layout
3. It chains multiple operations intelligently (spawn + position + rebuild)

---

## Proposed Changes

### Agent Bridge Core

---

#### [MODIFY] [unrealed_controller.py](file:///g:/UnrealTournament2004/AgentBridge/unrealed_controller.py)
- Add `execute_command_async()` method using `PostMessage` instead of `SendMessage`
- Add `generate_path_network()` method — intelligent grid-based PathNode placement
- Add `validate_path_nodes()` method — pre-flight duplicate/overlap/boundary checking
- Add timeout protection for `rebuild_level(paths=True)` with dialog auto-dismiss
- Modify `rebuild_level()` to use async dispatch for `PATHS BUILD`

#### [MODIFY] [tools_schema.py](file:///g:/UnrealTournament2004/AgentBridge/tools_schema.py)
- Add `generate_path_network` tool definition with room bounds and spacing parameters
- Update `rebuild_level` schema to note the async behavior for paths

#### [MODIFY] [server.py](file:///g:/UnrealTournament2004/AgentBridge/server.py)
- Add handler for `generate_path_network` tool in `_execute_tool_action()`
- Add `/v1/config/profiles` endpoint to list/update/create profiles
- Add `/v1/config/profiles/{name}/activate` endpoint for profile switching
- Add `/v1/models/fetch` POST endpoint that accepts ad-hoc provider+key for model listing

#### [MODIFY] [llm_engine.py](file:///g:/UnrealTournament2004/AgentBridge/llm_engine.py)
- Update system prompt with improved PathNode placement rules
- Add method for fetching models with custom (non-saved) credentials for the Settings UI

---

### Agent Chat UI (Tkinter)

---

#### [MODIFY] [tk_editor_chat.py](file:///g:/UnrealTournament2004/AgentBridge/tk_editor_chat.py)
- **Settings Button**: Add ⚙ gear button to header bar → opens Settings `Toplevel` window
- **Settings Window**: Full provider/API key/model configuration dialog with:
  - Provider dropdown (auto-fills base URL)
  - Masked API key entry with show/hide toggle
  - Base URL field
  - Model dropdown (populated via Fetch Models)
  - Temperature and Max Tokens fields
  - Tool calling and Vision checkboxes
  - Test Connection button → runs 5-step diagnostic with status display
  - Fetch Models button → queries provider and populates Model dropdown
  - Save & Apply button → persists to `AgentConfig.json` and activates profile
- **Quick Build Palette**: Replace 3 chips with categorized tabbed `ttk.Notebook`:
  - 8 category tabs with 4-9 buttons each
  - Each button sends an engineered prompt via `_fill_and_send()`
  - Compact 2-row button grid per tab
  - Scrollable if needed
- **Resize layout**: Make room for the larger palette at the bottom

---

## Verification Plan

### Automated Tests
```bash
# 1. Start bridge server and verify new endpoints
python AgentBridge/server.py &
curl http://127.0.0.1:9090/v1/config
curl http://127.0.0.1:9090/v1/models

# 2. Test path network generation (standalone)
python -c "from unrealed_controller import UnrealEdController; c = UnrealEdController(); print(c.generate_path_network((2048, 2048, 512), (0, 0, 0), spacing=384))"
```

### Manual Verification
1. Launch `Launch_UnrealEd_Agent.bat` — verify UEd 3.0 opens with the cockpit docked
2. Click ⚙ Settings → verify the Settings window opens with all fields
3. Enter an API key → click Test → verify 5-step diagnostic passes
4. Click Fetch Models → verify model dropdown populates with live models
5. Select model → click Save → verify `AgentConfig.json` is updated
6. Test Quick Build buttons — click "Desert Arena" → verify AI generates a desert level
7. Test "Path Node Grid" utility button → verify nodes are placed with proper spacing and no overlaps
8. Verify `PATHS BUILD` no longer freezes/crashes the editor (async dispatch + timeout)

---

## Open Questions

> [!IMPORTANT]
> **1. Quick Build Prompt Detail Level**: Should each Quick Build button send a brief prompt (letting the AI interpret creatively) or a highly detailed prompt with specific coordinates, textures, and mesh references? I recommend **detailed prompts** for reliability, but brief prompts give the AI more creative freedom.

> [!IMPORTANT]
> **2. PathNode Grid Spacing**: The default UT2004 PathNode spacing is ~512 UU. For smaller rooms (2048x2048), should we use tighter spacing (~256 UU) for better bot navigation, or standard spacing to reduce path build time?

> [!IMPORTANT]
> **3. Settings Window Scope**: Should the Settings window also include bridge server settings (HTTP port, WebSocket port, log polling interval) or stay focused on just LLM provider configuration?
