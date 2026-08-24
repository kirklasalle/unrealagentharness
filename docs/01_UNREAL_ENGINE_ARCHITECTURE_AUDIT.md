# Unreal Engine 1 / Unreal Tournament GOTY: Technical Architecture Audit

**Engine Version:** Unreal Engine 1 (v436 / OldUnreal v469 Patch Series)  
**Target Game:** Unreal Tournament: Game of the Year Edition  
**Audited Directory:** `G:\UnrealTournament`  
**Author:** Antigravity AI Engineering  
**Prepared For:** Kirk LaSalle (Lead Creator, UTron Project)

---

## 1. Executive Summary & Engine Overview

Unreal Engine 1 (UE1) is a hybrid C++ and UnrealScript game engine designed with a strictly modular, object-oriented subsystem architecture. The engine decouples low-level platform-specific execution (native C++ dynamic link libraries) from high-level gameplay rules, AI, state logic, and user interfaces (interpreted/bytecode UnrealScript `.u` packages).

### Core Architectural Layers

```
+-----------------------------------------------------------------------+
|                         Gameplay & Mod Layer                          |
|  (UTron, Botpack, UnrealShare, UnrealI, UMenu, UTMenu - *.u Packages) |
+-----------------------------------------------------------------------+
|                         UnrealScript VM (UVM)                         |
|      Bytecode Execution, State Machines, Replication Dispatching       |
+-----------------------------------------------------------------------+
|                         Native Engine Layer                           |
|       Engine.dll | Core.dll | Editor.dll | Render.dll | Window.dll    |
+-----------------------------------------------------------------------+
|                    Hardware Abstraction Subsystems                    |
|   Video Drivers: D3D9Drv, D3D11Drv, OpenGLDrv, XOpenGLDrv, VulkanDrv  |
|   Audio Drivers: Galaxy.dll, ALAudio.dll, Cluster.dll, OpenAL32.dll   |
|   Network Driver: IpDrv.dll (UDP TCP/IP)                              |
|   Input/Windowing: WinDrv.dll                                         |
+-----------------------------------------------------------------------+
|                        Host Operating System                          |
|                       Windows (Win32 / x86 / x64)                     |
+-----------------------------------------------------------------------+
```

---

## 2. Core Subsystem & Package Architecture (`Core.dll` / `Core.u`)

The foundational layer of UE1 is encapsulated in `Core.dll` and `Core.u`.

### 2.1 The `UObject` Hierarchy
Every persistent entity, texture, sound, script class, and level element inherits from `Core.Object`.
- **Object Flags (`EObjectFlags`):** Flags tracking lifecycle states (`RF_Transactional`, `RF_Public`, `RF_Transient`, `RF_Standalone`, `RF_Eliminated`).
- **Garbage Collection (GC):** UE1 utilizes a mark-and-sweep garbage collector. Objects not reachable through root references or outer chains are purged during level transitions or explicit calls to `CollectGarbage()`.
- **Name Table (`FName`):** All identifiers, class names, and property keys are indexed into an immutable global name hash table. Comparisons between `FName` values execute as single integer comparisons ($O(1)$) rather than string comparisons.

### 2.2 Unreal Package Structure (`.u`, `.utx`, `.uax`, `.umx`, `.unr`)
All Unreal asset files share the identical underlying binary package format:
1. **Package File Header:**
   - Magic identifier: `0x9E2A83C0` (Unreal Package Signature).
   - Package version (e.g., 68 for UT v436, updated compatibility in v469).
   - Counts and file offsets for the Name Table, Import Table, and Export Table.
2. **Name Table:** Serialized list of all string tokens referenced within the package.
3. **Import Table:** References to external objects residing in other packages (e.g., `Engine.Pawn` referenced by `UTron.Flynn`).
4. **Export Table:** Index of all objects serialized into this package file, including class definitions, bytecode offsets, texture MIP maps, audio waveforms, or BSP polygon trees.

---

## 3. Engine Subsystem & Gameplay Lifecycle (`Engine.dll` / `Engine.u`)

### 3.1 The `Actor` Hierarchy
All entities capable of being spawned, rendered, ticked, or placed into a level inherit from `Engine.Actor`.

```
Core.Object
  └── Engine.Actor
        ├── Engine.Pawn (Characters, Bots, Players)
        │     ├── Engine.PlayerPawn (Human Player Controllers)
        │     │     └── Botpack.TournamentPlayer
        │     │           └── UTron.Flynn / UTron.Tron / UTron.Sark
        │     └── Botpack.Bot (AI Controlled Combatants)
        ├── Engine.Inventory (Weapons, Pickups, Powerups)
        │     ├── Engine.Weapon
        │     │     └── UTron.IdentityDisc / UTron.TankGun
        │     └── Engine.Pickup
        ├── Engine.Info
        │     ├── Engine.GameInfo (Game Rules / Gametypes)
        │     │     └── Botpack.TournamentGameInfo
        │     │           ├── Botpack.DeathMatchPlus
        │     │           └── UTron.DiscArena / UTron.TankGame
        │     └── Engine.ZoneInfo (Environment Properties)
        ├── Engine.Projectile
        │     └── UTron.RecoProj / UTron.MPLPproj
        └── Engine.Decoration / Keypoint / Triggers / NavigationPoint
```

### 3.2 The Tick Pipeline
During each rendering frame, `Engine.GameEngine` executes a deterministic tick cycle:
1. **Pre-Tick Input Processing:** Mouse and keyboard inputs polled via `WinDrv.dll` and translated into `PlayerPawn.PlayerInput()`.
2. **Actor Ticking (`Actor.Tick(DeltaTime)`):**
   - Autonomous actors update states and animations.
   - AI Pawns evaluate perception, pathfinding, and decision trees (`Bot.WhatToDoNext()`).
   - Timers (`SetTimer`) decrement and dispatch timer events.
3. **Physics & Collision Resolution:**
   - Movement modes evaluated (`PHYS_Walking`, `PHYS_Falling`, `PHYS_Flying`, `PHYS_Rotating`, `PHYS_Custom`).
   - Trace raycasts and bounding box / cylinder collision detection against BSP world geometry and other actors.
4. **Replication & Network Dispatch:**
   - Server polls dirty properties on replicated actors and packages network updates into UDP datagrams.
5. **Post-Tick & Rendering:**
   - Camera viewports calculated.
   - BSP, dynamic mesh, particle, and Canvas HUD elements submitted to the active rendering driver.

---

## 4. Networking & Replication Architecture (`IpDrv.dll`)

Unreal Engine 1 pioneered authoritative client-server multiplayer replication over UDP.

### 4.1 Client-Server Network Roles
Every actor has a local `Role` and a `RemoteRole`:
- `ROLE_Authority`: Full authoritative ownership (always on the server).
- `ROLE_SimulatedProxy`: Client simulates physics, prediction, and animation locally between server sync frames.
- `ROLE_AutonomousProxy`: Controlled directly by local player input with client-side prediction and server reconciliation.
- `ROLE_DumbProxy`: Client only renders positions and animations explicitly dictated by server updates.

### 4.2 Replication Statements
In UnrealScript classes, the `replication` block defines variables and functions synchronized across the network:
```unrealscript
replication
{
    // Replicate from server to client if dirty and role is authoritative
    reliable if ( Role == ROLE_Authority )
        Health, DiscState, bShieldActive;

    // Remote Procedure Call (RPC) from client to server
    reliable if ( Role < ROLE_Authority )
        ServerFireDisc, ServerAltAction;
}
```

---

## 5. Map & World Geometry Architecture (`.unr` / BSP)

UE1 maps (`.unr`) are constructed using **Constructive Solid Geometry (CSG)** and **Binary Space Partitioning (BSP)**.

1. **Subtractive CSG:** The world begins as solid infinite matter. Level designers subtract brushes to create interior rooms and add brushes for structural details.
2. **BSP Tree Generation:** The editor slices polygon geometry into a binary partitioning tree, enabling real-time hidden surface removal and front-to-back polygon rendering.
3. **Zone Portals & Occlusion:** Dividing levels into zones via invisible portal sheets allows the engine to skip rendering entire rooms when occluded, and allows unique environmental physics (e.g., zero-gravity or water zones).
4. **Lighting:** Static lightmaps (baked luxels) stored in texture memory alongside dynamic actor lighting calculations.

---

## 6. Rendering Subsystem (`Render.dll` + Driver DLLs)

UE1 isolates rendering through a pluggable hardware driver architecture:
- **`D3D9Drv.dll` / `D3D11Drv.dll`:** Modern DirectX 9/11 rendering with shader-based gamma and widescreen support.
- **`OpenGLDrv.dll` / `XOpenGLDrv.dll`:** Modern OpenGL renderers with high-resolution texture filtering and frame stabilization.
- **`VulkanDrv.dll`:** Next-gen Vulkan API integration provided by the OldUnreal v469 patch.
- **`SoftDrv.dll`:** Legacy CPU-based software renderer.
- **`GlideDrv.dll`:** Legacy 3dfx Glide driver.

---

## 7. Audio Subsystem (`Galaxy.dll` / `ALAudio.dll` / `Cluster.dll`)

- **Music (`.umx`):** High-performance tracker module music formats (Impulse Tracker `.it`, FastTracker 2 `.xm`, Scream Tracker 3 `.s3m`, ProTracker `.mod`). These provide interactive multi-channel adaptive audio with minimal memory overhead.
- **Sound Effects (`.uax`):** PCM WAV digital audio clips (typically 22,050 Hz / 44,100 Hz, 16-bit mono) with 3D spatialization, pitch variation, and doppler simulation.
- **Modern OldUnreal Drivers:** `ALAudio.dll` leverages modern OpenAL hardware acceleration, EAX reverb emulation, and multichannel surround sound (5.1/7.1).

---

## 8. User Interface Subsystem (`UWindow` / `UMenu` / `UTMenu`)

Unreal Tournament features a complete windowing GUI framework built entirely in UnrealScript:
- **`UWindowRootWindow`:** Top-level viewport container managing mouse capture, focus, and draw passes.
- **`UWindowFramedWindow`:** Moveable, resizable dialog windows with title bars and close buttons.
- **`UWindowDialogClientWindow`:** Panel containing buttons, sliders, checkboxes, combos, and text fields.
- **`UTMenu` & `UTronMenu`:** Custom themed menu bars, server browsers, bot match selectors, and HUD extensions.
