# UnrealEd 3.0 Agent Bridge API Reference (OpenAPI 3.0 & WebSocket)

The **UnrealEd Agent Bridge Server** exposes an asynchronous HTTP REST API (port `9090`) and a real-time WebSocket event bus (port `9091`) allowing external AI agents, Python scripts, and MCP servers to control UnrealEd 3.0.

Base URL: `http://127.0.0.1:9090`  
WebSocket URL: `ws://127.0.0.1:9091`

---

## 1. REST Endpoints

### 1.1 `POST /v1/exec` — Execute UnrealEd Commands
Executes one or more raw UnrealEd 3 console commands sequentially in `UEditorEngine`.

**Request Body:**
```json
{
  "commands": [
    "BRUSH BUILD BOX X=1024 Y=1024 Z=512",
    "BRUSH SUBTRACT",
    "POLY SELECT ALL",
    "POLY SET TEXTURE=HumanFloor.Floors.metal_flr01",
    "ACTOR ADD CLASS=Light",
    "MAP REBUILD",
    "PATHS BUILD"
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "execution_time_ms": 84.2,
  "executed_count": 7,
  "results": [
    {"command": "BRUSH BUILD BOX...", "status": "OK", "log": ""},
    {"command": "BRUSH SUBTRACT", "status": "OK", "log": "Subtracted brush."},
    {"command": "MAP REBUILD", "status": "OK", "log": "BSP built: 6 polys."},
    {"command": "PATHS BUILD", "status": "OK", "log": "1 PathNodes connected."}
  ]
}
```

---

### 1.2 `GET /v1/state` — Get Editor & Level State
Returns the current active level status, actor counts, and selection information.

**Response (200 OK):**
```json
{
  "connected": true,
  "unrealed_pid": 14220,
  "active_map": "DM-1on1-Mixer.ut2",
  "actor_count": 142,
  "brush_count": 18,
  "selected_actors": ["Light_4", "PathNode_12"],
  "builder_brush": {
    "shape": "Box",
    "dimensions": [1024, 1024, 512]
  },
  "grid": {
    "size": 16,
    "enabled": true
  }
}
```

---

### 1.3 `GET /v1/actors` — Query Level Actors
Retrieves a list of actors in the active level with optional filtering.

**Query Parameters:**
* `class` (optional, string): Filter by class name (e.g. `PathNode`, `Light`, `PlayerStart`).
* `tag` (optional, string): Filter by actor tag.

**Response (200 OK):**
```json
{
  "count": 2,
  "actors": [
    {
      "name": "PathNode_0",
      "class": "PathNode",
      "location": [0, 0, 32],
      "tag": "None"
    },
    {
      "name": "PlayerStart_0",
      "class": "PlayerStart",
      "location": [256, 0, 40],
      "tag": "RedSpawn"
    }
  ]
}
```

---

### 1.4 `POST /v1/actors/spawn` — Parametric Actor Spawning
Spawns an actor of a given class at exact 3D coordinates.

**Request Body:**
```json
{
  "actor_class": "XWeapons.ShockRiflePickup",
  "location": [512, 256, 40],
  "properties": {
    "DrawScale": 1.2,
    "Tag": "SuperWeapon"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "spawned_name": "ShockRiflePickup_0",
  "actor_class": "XWeapons.ShockRiflePickup",
  "location": [512, 256, 40]
}
```

---

### 1.5 `POST /v1/bsp/create` — Parametric CSG Room Builder
Constructs a complete subtractive or additive room with dimensions and optional lighting/texture settings.

**Request Body:**
```json
{
  "shape": "Box",
  "operation": "Subtract",
  "dimensions": [2048, 2048, 512],
  "location": [0, 0, 0],
  "texture": "Industrial.Walls.metalwall01",
  "add_light": true,
  "light_brightness": 180
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Created 2048x2048x512 Subtraction Room with Light at [0, 0, 0]"
}
```

---

### 1.6 `POST /v1/build` — Trigger Rebuilding Pipeline
Executes geometry, lighting, or path rebuilding operations.

**Request Body:**
```json
{
  "build_geometry": true,
  "build_lighting": true,
  "build_paths": true,
  "check_errors": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "geometry_status": "OK",
  "lighting_status": "OK",
  "paths_status": "OK",
  "error_check": {
    "total_errors": 0,
    "warnings": 0
  }
}
```

---

### 1.7 `GET /v1/viewport/screenshot` — 3D Viewport Capture
Captures the active perspective viewport as a high-resolution PNG image for multimodal vision models.

**Response (200 OK):**
* `Content-Type: image/png`
* Binary PNG image stream.

---

### 1.8 `POST /v1/game/test` — Instant Match Playtesting
Launches a standalone playtest instance of UT2004 with the current map.

**Request Body:**
```json
{
  "map": "Current",
  "game_type": "UTron2004.UTronArcadeClassic",
  "bots": 4,
  "spectator": false
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "launched_pid": 16840,
  "command_line": "UT2004.exe Current.ut2?game=UTron2004.UTronArcadeClassic?NumBots=4"
}
```

---

## 2. WebSocket Real-Time Event Bus (`ws://127.0.0.1:9091`)

Connect to the WebSocket endpoint for continuous real-time streaming:

### Event Types Dispatched:
1. `log_entry`: Streamed lines from `GLog` and `Editor.log`.
   ```json
   {"event": "log_entry", "timestamp": 1724184000.12, "source": "UEditorEngine", "line": "BSP Rebuilt: 12 Polygons, 6 Nodes."}
   ```
2. `editor_connected`: Emitted when the bridge establishes contact with `UnrealEd.exe`.
   ```json
   {"event": "editor_connected", "pid": 14220}
   ```
3. `chat_token`: Streamed LLM inference response tokens for the In-Editor Chat Cockpit.
   ```json
   {"event": "chat_token", "delta": "I have created the 2048x2048 arena."}
   ```
