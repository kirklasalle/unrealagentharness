# UnrealEd 3.0 & Unreal Engine 2.5 Architecture Guide

---

## 1. Engine & Subsystem Architecture

Unreal Engine 2.5 is a hybrid C++ and UnrealScript engine designed around object reflection, package serialization, and modular subsystems.

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                         UnrealEd 3.0 Runtime Stack                          │
 └─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ UnrealEd.exe  (Win32 Process Launcher & Window Frame)                       │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ UnrealEdDLL.dll (Win32 GUI, Viewports, Toolbars, Asset Browsers, Status Bar) │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ Editor.dll     (UEditorEngine, CSG BSP Compiler, Raytracer, Path Network)   │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ Engine.dll     (ULevel, UWorld, AActor, APawn, UPrimitive, UCanvas)          │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ Core.dll       (UObject, FName, FString, TArray, Garbage Collector, Memory) │
 └─────────────────────────────────────────────────────────────────────────────┘
```

### Core Subsystems
1. **`Core.dll`**: The foundational object system providing the base class `UObject`, garbage collection, name hashing table (`FName`), dynamic arrays (`TArray`), dynamic strings (`FString`), serialization streams (`FArchive`), and native error logging (`FOutputDevice` / `GLog`).
2. **`Engine.dll`**: Core gameplay and rendering framework:
   * `ULevel`: Holds all actors in the active level (`TArray<AActor*> Actors`).
   * `AActor`: Root class for all placeable entities (Pawns, Lights, Triggers, Pickups, Geometry Brushes).
   * `UCanvas`: 2D rendering canvas used by HUDs and editor interfaces.
3. **`Editor.dll` (`UEditorEngine`)**: Editor backend extending `UEngine`:
   * **CSG BSP Compiler**: Executes boolean constructive solid geometry operations (`Add`, `Subtract`, `Intersect`, `Deintersect`).
   * **Lighting Engine**: Raytracing and radiosity lighting compiler calculating direct light, ambient occlusion, and shadow maps.
   * **Navigation Mesh Compiler**: Computes path reachability tables between `PathNode`, `PlayerStart`, and pickup locations.
   * **Transaction Manager**: Manages undo/redo transaction buffers (`Trans->Begin()`, `Trans->End()`, `Trans->Undo()`).
4. **`UnrealEdDLL.dll`**: The Win32/MFC user interface layer containing 2D/3D viewport windows, the texture browser, static mesh browser, sound browser, and the bottom status/command bar.
5. **`Window.dll` / `WinDrv.dll`**: Low-level Win32 platform drivers handling window creation, message loops, keyboard/mouse input, and Direct3D viewport rendering.

---

## 2. The `UEditorEngine::Exec` Command Pipeline

Every operation in UnrealEd 3.0 flows through a centralized text execution dispatcher:

```cpp
// Conceptual Native C++ Signature inside Editor.dll:
UBOOL UEditorEngine::Exec( const TCHAR* Cmd, FOutputDevice& Ar=*GLog );
```

When a user or tool enters a command into the UnrealEd command bar:
1. `UnrealEdDLL.dll` retrieves the string from the `Edit` control.
2. The string is passed to `GEditor->Exec(Cmd, *GLog)`.
3. `UEditorEngine::Exec` parses the command token (e.g. `ACTOR`, `BRUSH`, `MAP`, `POLY`, `LIGHT`, `PATHS`).
4. The requested engine operation is executed synchronously on the main thread.
5. Status and diagnostic output are piped directly to `GLog`, which appends to `System\Editor.log` and the in-editor log window.

---

## 3. The Dual-Layer Agent Bridge Architecture

The UnrealEd AI Agent system operates through a **Dual-Layer Bridge**:

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                         EXTERNAL / IN-EDITOR CLIENT                         │
 │        (Chat Cockpit Web UI, Python Script, or Remote AI Agent)             │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │ HTTP REST / WebSocket JSON
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                FASTAPI ASYNCHRONOUS BRIDGE SERVER (Port 9090)               │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │ - /v1/exec, /v1/state, /v1/actors, /v1/bsp/create, /v1/build, /v1/game/test │
 │ - Multi-Provider LLM Engine (Gemini, Claude, GPT-4, Ollama, DeepSeek)       │
 │ - WebSocket Broadcast Hub (60 FPS Event / Log Stream)                       │
 └───────────────────┬─────────────────────────────────────┬───────────────────┘
                     │                                     │
                     ▼                                     ▼
 ┌───────────────────────────────────────┐ ┌───────────────────────────────────┐
 │   Win32 UI Automation Controller      │ │    C++ Native DLL Plugin Hook     │
 │ (pywin32 / SendMessage / Log Tail)    │ │ (Direct GEditor->Exec & Memory)   │
 └───────────────────┬───────────────────┘ └───────────────────┬───────────────┘
                     │                                         │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                     UnrealEd 3.0 Native Process Space                       │
 │  - Main Frame Window: WUnrealEd                                             │
 │  - Command Bar Edit Control (Child of Status/Toolbar)                       │
 │  - Log Stream: GLog -> System\Editor.log                                    │
 │  - Viewports: Direct3D9 Viewport Surface                                    │
 └─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Win32 UI Handle & Command Injection Engine
* **Window Discovery**: Scans top-level Win32 windows matching `WUnrealEd` or process `UnrealEd.exe`.
* **Command Bar Targeting**: Uses `FindWindowEx` to locate the child `Edit` control in the lower toolbar area.
* **Message Dispatch**: Sends `WM_SETTEXT` with the command string followed by `WM_KEYDOWN(VK_RETURN)` and `WM_KEYUP(VK_RETURN)` to trigger immediate native execution.
* **Real-time Log Interception**: Runs an asynchronous file watcher on `System\Editor.log` with sub-millisecond line delta parsing, stripping `Cmd:` tags and broadcasting execution logs to WebSocket clients.

### 3.2 Viewport Framebuffer Capture Engine
* Locates the 3D perspective viewport child window (`WViewportWindow` / Direct3D render target).
* Uses Win32 GDI `BitBlt` / `PrintWindow` or Direct3D surface copying to capture clean RGB frames.
* Encodes frames to optimized PNG buffers for transmission to multimodal AI models (Gemini 2.5, GPT-4o, Claude 3.7) to enable visual spatial reasoning.

---

## 4. T3D Serialization & Builder Brush CSG Pipeline

Unreal Engine 2.5 supports bidirectional text serialization through the **T3D (Text 3D)** format. The bridge utilizes two distinct T3D workflows:

### 4.1 Builder Brush PolyList Pipeline (`BRUSH IMPORT`)
To guarantee 100% engine stability and avoid internal `ULevelFactory::FactoryCreateText` -> `bspValidateBrush` linkage failures during runtime level generation, the bridge generates raw `PolyList` brush definitions loaded directly into UnrealEd's active builder brush:

```unreal
Begin PolyList
   Begin Polygon Item=Floor Flags=0
      Origin   -1024.000000,+1024.000000,-256.000000
      Normal   +0.000000,+0.000000,-1.000000
      TextureU +1.000000,+0.000000,+0.000000
      TextureV +0.000000,-1.000000,+0.000000
      Vertex   -1024.000000,+1024.000000,-256.000000
      Vertex   +1024.000000,+1024.000000,-256.000000
      Vertex   +1024.000000,-1024.000000,-256.000000
      Vertex   -1024.000000,-1024.000000,-256.000000
   End Polygon
   ... [Remaining 5 Watertight Box Polygons] ...
End PolyList
```

#### CSG Execution Lifecycle:
1. **Positioning**: `BRUSH MOVETO X=... Y=... Z=...` places the builder brush at the exact world origin.
2. **Import**: `BRUSH IMPORT FILE="BrushShape.t3d" MERGE=0 FLAGS=0` parses vertices into the red builder brush.
3. **CSG Commit**: `BRUSH SUBTRACT` or `BRUSH ADD` carves or adds the geometry into the world BSP tree.
4. **Actor Placement**: `ACTOR ADD CLASS=<Class>` places lights, player starts, and path nodes.
5. **Compilation**: `GEOMETRY REBUILD` + `LIGHT APPLY` + `FLUSH` compiles the BSP tree and bakes lighting.

### 4.2 Full Map T3D Inspection & Export (`MAP EXPORT`)
Executing `MAP EXPORT FILE="dump.t3d"` exports the full level hierarchy (Actors, properties, brush polygons) for multimodal AI level evaluation, actor counting, and connectivity auditing.

---

## 5. Native Dockable Cockpit Architecture

The **Native Dockable Cockpit** (`AgentBridge/agent_ui_native.py`) runs as a dedicated Win32 process using a Tkinter/ctypes bridge:

1. **Auto-Dock Tracking**: Polls the parent `WUnrealEd` window rect at 20 Hz (`GetWindowRect`). Automatically snaps to the right border of UnrealEd whenever the editor moves, resizes, or minimizes.
2. **Floating Toggle**: Allows the user to unpin (`🪟 Floating`) to position the chat interface across secondary monitors or anywhere on the desktop.
3. **Zero Performance Overhead**: Pure Win32 event pump running independently with zero WebView or Chromium CPU/RAM overhead, ensuring UnrealEd maintains 60+ FPS.
