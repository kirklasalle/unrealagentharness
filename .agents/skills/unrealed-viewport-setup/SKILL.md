---
name: unrealed-viewport-setup
description: World-class default Unreal Editor viewport setup and configuration skill (Top, Front, and Side orthographic viewports scaled to full extents across the top row, and Dynamic Light 3D perspective viewport across the bottom row).
---

# UnrealEd Standard 4-Viewport Setup Skill

## Overview

In the **Unreal Agent Harness**, the standard, world-class Unreal Editor viewport configuration provides immediate 360-degree spatial awareness and real-time lighting fidelity. 

The editor workspace is structured into a **Top Tri-View Row** (Orthographic wireframe views scaled to full level extents) and a **Bottom Panoramic 3D Viewport** (Real-time Dynamic Lighting).

```
┌──────────────────────────┬──────────────────────────┬──────────────────────────┐
│         Top (XY)         │        Front (XZ)        │        Side (YZ)         │
│     (Orthographic)       │     (Orthographic)       │     (Orthographic)       │
│  [T] Mode Active, 1/3 W  │  [F] Mode Active, 1/3 W  │  [S] Mode Active, 1/3 W  │
│  Scaled to Full Extents  │  Scaled to Full Extents  │  Scaled to Full Extents  │
├──────────────────────────┴──────────────────────────┴──────────────────────────┤
│                               Dynamic Light (3D)                               │
│                         (Real-Time Dynamic Lighting)                           │
│                          Full Width (1.0 W), 1/2 H                             │
│                  Elevated 3/4 Isometric Perspective Angle                      │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Viewport Geometry & Coordinate Mappings

The viewport regions are mapped as normalized percentage boundaries within the UnrealEd client area:

| Viewport Name | Rendering Mode | `RendMap` ID | Client Bounding Box `(x%, y%, w%, h%)` | Function & Visual Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`Top`** | `REN_OrthXY` | `13` | `(0.000, 0.000, 0.333, 0.500)` | Top-down $XY$ perimeter, paths, alignment, brush placement. |
| **`Front`** | `REN_OrthXZ` | `14` | `(0.333, 0.000, 0.334, 0.500)` | Front-facing $XZ$ elevation, tower heights, water table levels. |
| **`Side`** | `REN_OrthYZ` | `15` | `(0.667, 0.000, 0.333, 0.500)` | Side-facing $YZ$ canyon depth, bridge slopes, terrain grade. |
| **`Dynamic Light`** | `REN_DynLight` | `5` | `(0.000, 0.500, 1.000, 0.500)` | 3D textured perspective with real-time lightmaps & shadows. |

---

## Configuration Automation

### 1. `UnrealEd.ini` Initialization
The harness automatically enforces `Config=3` within the active engine's `UnrealEd.ini`:

```ini
[Viewports]
Style=0
Config=3

[U2Viewport0]
Active=1
RendMap=13
PctLeft=0.000000
PctTop=0.000000
PctRight=0.333333
PctBottom=0.500000

[U2Viewport1]
Active=1
RendMap=14
PctLeft=0.333333
PctTop=0.000000
PctRight=0.333334
PctBottom=0.500000

[U2Viewport2]
Active=1
RendMap=15
PctLeft=0.666667
PctTop=0.000000
PctRight=0.333333
PctBottom=0.500000

[U2Viewport3]
Active=1
RendMap=5
PctLeft=0.000000
PctTop=0.500000
PctRight=1.000000
PctBottom=0.500000
```

### 2. Runtime Execution Commands
Upon map generation or level rebuild, dispatch the following commands via `EngineController`:
```text
MODE DYNAMICLIGHT
CAMERA ALIGN
VIEWPORT REDRAW
```

---

## Multimodal Vision & QA Integration

1. **Quadrant Capture**: Use `VisionInspector.capture_viewport(hwnd, viewport="top"|"front"|"side"|"dynamic_light")` to extract exact viewports.
2. **Full Quad Context**: Use `VisionInspector.capture_standard_quad_view(hwnd)` to package all 4 views for multimodal LLM spatial evaluation.
3. **Graph Training Memory**: Every viewport capture and layout verification event automatically records a training node and edge in `MemoryEngine`.
