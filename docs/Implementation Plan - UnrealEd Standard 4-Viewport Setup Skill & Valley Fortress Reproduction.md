# Implementation Plan: UnrealEd Standard 4-Viewport Setup Skill & Valley Fortress Reproduction

Deeply analyze `agentharness_113..png` and `Builderbutton_valley_01.jpg`, standardize the 4-viewport layout (Top, Front, Side + Dynamic Light) as the permanent default across the Unreal Agent Harness, implement a dedicated agent skill, and provide the complete procedural blueprint for reproducing the Valley Fortress map.

---

## 1. Deep Analysis of Editor & Reference Artifacts

### 1.1 Deep Deconstruction of `agentharness_113..png`

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

1. **Top Row (Orthographic Tri-View)**:
   - **Left Viewport (`Top`)**: Pure orthographic top-down wireframe ($XY$ plane). Mode selector `T` is active. Zoomed and scaled to fit the entire map bounding box ($X: -2304 \to +2304, Y: -2304 \to +2304$). Shows the outer perimeter, river cut, bridge crossings, tower foundations, and tree placements.
   - **Center Viewport (`Front`)**: Pure orthographic front-facing wireframe ($XZ$ plane). Mode selector `F` is active. Shows vertical elevations, tower heights, bridge elevation differences, and ceiling bounding limits.
   - **Right Viewport (`Side`)**: Pure orthographic side-facing wireframe ($YZ$ plane). Mode selector `S` is active. Confirms alignment across the canyon depth and slope profiles.
2. **Bottom Row (Full-Width 3D Viewport)**:
   - **`Dynamic Light` Viewport**: Spans the entire bottom 50% of the editor window ($100\%$ width). Mode selector `D` (Dynamic Light) is active, rendering real-time lightmaps, vertex lighting, and shadow casting. Camera is pitched down at $\sim 35^\circ$ in an elevated perspective overlooking the valley floor.
3. **Current Geometry & Lighting Critique**:
   - *Current State*: The map currently consists of a flat-walled box enclosure with vertical cylindrical tower brushes and a shallow river cut.
   - *Deficiencies*: Flat ceiling plane with visible stone texture instead of an open skybox dome; flat sheer walls without stepped mountain shelves or waterfall recesses; castle lacks architectural gatehouse portals, crenellations, and roofs.

---

### 1.2 Deep Deconstruction of `Builderbutton_valley_01.jpg`

```
                                  [ SKY DOME / ALPINES ]
                              (High clouds, distant peaks)
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       [ WEST CLIFFS & WATERFALLS ]                    [ EAST CASTLE BLUFF ]
     • Steep granite rock terraces                   • Massive promontory keep
     • Cascading waterfall sheets                    • 4 Octagonal bastion towers
     • Cliff peak watchtowers                        • Fortified arched gatehouse
     • Dense pine tree groves                        • Upper Drawbridge landing
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           ▼
                                [ CENTRAL RIVER GORGE ]
                              • Deep chasm / river bed
                              • Lower Arched Stone Bridge
                              • Upper Wooden Drawbridge
                              • Framing pine trees & boulders
```

- **Red Operator Markup & Edge Detection**:
  - *Red Oval (Top)*: Defines the open sky dome boundary ($\approx 35-40\%$ of upper composition). Must be realized via `SkyZoneInfo` and `FakeBackdrop` surfaces.
  - *Red Oval (Upper Right)*: Defines the East Fortress mass and tower heights on the high bluff.
  - *Red Angle Brackets & Lines (Left)*: Mark the sheer stepped descent of the West cliff and the vertical cascade channel of the waterfall.
  - *Red Lines (Center & Bridges)*: Mark the lower arched stone bridge span, the upper wooden drawbridge approach, and the central river canyon slope.

---

## 2. Proposed System Changes

### Component 1: Default Viewport Configuration & Vision Inspector
- **[MODIFY] [core/vision_inspector.py](file:///d:/Projects/unrealagentharness/core/vision_inspector.py)**:
  - Update `VIEWPORT_QUADRANTS` to precisely map the 3-top + 1-bottom layout:
    ```python
    VIEWPORT_QUADRANTS = {
        "top": (0.0, 0.0, 0.3333, 0.5),
        "front": (0.3333, 0.0, 0.3334, 0.5),
        "side": (0.6667, 0.0, 0.3333, 0.5),
        "perspective": (0.0, 0.5, 1.0, 0.5),
        "dynamic_light": (0.0, 0.5, 1.0, 0.5),
    }
    ```
  - Add `capture_all_standard_viewports()` to extract and label all 4 viewports simultaneously for multimodal LLM spatial evaluation.

- **[MODIFY] [core/engine_controller.py](file:///d:/Projects/unrealagentharness/core/engine_controller.py)**:
  - Add `configure_standard_viewports()`:
    - Writes the 3-top-1-bottom layout to `UnrealEd.ini` (`Config=3`, `RendMap=13` for Top, `14` for Front, `15` for Side, `5` for Dynamic Light).
    - Dispatches camera extents and mode commands to ensure viewports zoom to full level extents upon load.

- **[MODIFY] [core/tools_schema.py](file:///d:/Projects/unrealagentharness/core/tools_schema.py)**:
  - Add schema for `configure_unrealed_viewports` and `capture_standard_quad_view`.

---

### Component 2: Dedicated Viewport Setup Skill
- **[NEW] [.agents/skills/unrealed-viewport-setup/SKILL.md](file:///d:/Projects/unrealagentharness/.agents/skills/unrealed-viewport-setup/SKILL.md)**:
  - Create a world-class Antigravity Agent Skill defining the 4-viewport standard:
    - Viewport geometry, percentage coordinates, render modes (`REN_DynLight`, `REN_OrthXY`, `REN_OrthXZ`, `REN_OrthYZ`).
    - INI configuration keys and console command orchestration (`CAMERA ALIGN`, `MAP ZOOM EXTENTS`).
    - QA verification procedure for viewport alignment.

- **[MODIFY] [core/skill_genesis.py](file:///d:/Projects/unrealagentharness/core/skill_genesis.py)**:
  - Register `unrealed_viewport_setup` permanently into the lifelong SQLite memory store on bootstrap.

---

### Component 3: Valley Fortress Geometry Synthesis Blueprint
- **[MODIFY] [core/formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py)**:
  - Refine `generate_ut99_verdant_mountain_valley` / Valley Fortress generator:
    1. **Skybox Chamber**: Isolated cube at `(0, 0, 4608)` with `SkyZoneInfo` + `FakeBackdrop` (`Flags=128`) ceiling.
    2. **Stepped West Mountain Terraces & Waterfalls**: Additive stepped granite rock shelves with vertical sheet brushes (`GenFluid.Water1`).
    3. **Central Deep River Chasm**: Carved river bed with `GenFluid.Water1` surface and rock embankments.
    4. **East Promontory Fortress**: Stone keep with gatehouse archway, octagonal towers (`sides=8`), battlements, and interior hall.
    5. **Dual Bridges**: Lower arched stone masonry bridge + Upper wooden timber drawbridge.
    6. **Vegetation, Torches & Lighting**: Clustered pine trees (`UnrealShare.Tree1-3`), torch sconces (`TorchFlame`), and warm/cool light balance.
    7. **Botpack AI Navigation Lattice**: 24-node path network with validated non-embedded `PlayerStart` points.

---

## 3. Verification Plan

### Automated Verification
1. Run `python test_harness.py` to ensure all 117+ unit tests pass without regressions.
2. Verify `VIEWPORT_QUADRANTS` calculations and crop dimensions against synthetic and real editor captures.
3. Validate T3D actor manifests for zero player start collisions and valid reachability graphs.

### Manual / In-Editor Verification
1. Inspect UnrealEd with active layout: verify Top, Front, Side viewports across the top row and Dynamic Light across the bottom.
2. Verify visual fidelity in perspective view: open alpine skybox rendered through `FakeBackdrop`, multi-tower fortress, dual bridges, cascading waterfall, and pine tree clusters.
