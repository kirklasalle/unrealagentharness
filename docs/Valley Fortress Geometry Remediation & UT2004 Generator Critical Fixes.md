# Valley Fortress Geometry Remediation & UT2004 Generator Critical Fixes

Based on the forensic analysis of [agentharness_114.png](file:///d:/Projects/unrealagentharness/screengrabs/agentharness_114.png) against the gold standard [Builderbutton_valley_01.jpg](file:///d:/Projects/unrealagentharness/public_html/images/Builderbutton_valley_01.jpg), this plan addresses **7 critical geometry engineering failures** in the UT2004 Valley Fortress generator.

---

## Visual Audit — Identified Defects (Red-Circled Areas in `agentharness_114.png`)

### What the Screenshot Reveals

The 4-viewport layout (Top, Front, Side wireframe + Dynamic Light 3D) exposes these failures:

| # | Defect | Viewport Evidence | Root Cause | Severity |
|:--:|:---|:---|:---|:---:|
| 1 | **Ceiling shows opaque grey tiles instead of skybox** | Dynamic Light: large red circle at top-center shows flat grey checkerboard ceiling instead of sky | UT2004 generator uses `t_sky` texture on ceiling but **never applies `FakeBackdrop\|Unlit` flags** (`4194432`). The UE1 generator does this correctly. | 🔴 **CRITICAL** |
| 2 | **Castle is floating — no ground contact** | Front/Side viewports: castle brushes hover above floor level; gap visible between bluff bottom and canyon floor | Bluff center is at `Z=-512` with height 1024, so base is at `Z=-1024` = floor_z. **But** the bluff is placed at `X=1280` while the valley floor is centered at `X=0` — the bluff's additive solid sits *within* the subtracted canyon void and its bottom edge aligns with the canyon floor, so it **appears to float** because no terrain ramps or cliff faces visually connect it to the ground. | 🔴 **CRITICAL** |
| 3 | **No textures visible — everything is default checker** | Dynamic Light: all surfaces show the default UE checkerboard pattern | UT2004 textures reference packages like `AntalusTextures`, `AbaddonArchitecture`, `ArboreaArchitecture` — but the `OBJ LOAD` commands reference `.utx` extensions. **The texture package names may not resolve in all UT2004 installs**, or the texture group paths (`AntalusTextures.Terrain.Dirt1`) may be invalid for the installed version. | 🔴 **CRITICAL** |
| 4 | **River gorge allows players to fall off the map** | Top viewport: river gorge extends to full valley length; Side: gorge floor is open-ended | The gorge is a full-length subtract (`1024 x 4608 x 256`) with no blocking volumes or kill zones at the Y extremes. Players walking along the river can fall off the world edge. | 🟡 **HIGH** |
| 5 | **Invisible walls / purposeless geometry** | Side viewport: multiple small brush outlines visible at edges that serve no gameplay or visual purpose | Multiple subtracted brushes (waterfalls, corridors) positioned partially outside the main valley bounds create BSP holes and invisible collision walls. | 🟡 **HIGH** |
| 6 | **No sky opening brush for UT2004** | Comparing UE1 vs UT2004 generator code: UE1 has `f_sky_opening` brush with `FakeBackdrop\|Unlit` flags to remove the opaque ceiling; UT2004 does not | The UT2004 generator relies solely on the ceiling texture being set to `t_sky`, but never flags the ceiling surface with `PF_FakeBackdrop` (`4194304`) or `PF_Unlit` (`2`). Without these flags, the sky texture renders as an opaque flat image. | 🔴 **CRITICAL** |
| 7 | **Missing semi-solid detail brushes** | The UE1 generator has 12+ semi-solid decorative brushes (buttresses, terraces, merlons, window frames, bridge piers, stepping stones, waterfall sheets, river surfaces). The UT2004 generator has **zero** semi-solid detail. | The UT2004 generator was built at 75% budget but skipped all decorative semi-solids that give the Valley Fortress its visual richness. | 🟡 **HIGH** |

---

## Proposed Changes

### Component 1: Skybox & Ceiling Fix (Defects 1, 6)

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py)

**Problem**: The `generate_ut2004_verdant_mountain_valley` function never applies `FakeBackdrop|Unlit` flags to the main valley ceiling or creates a sky opening brush. The UE1 version does this correctly.

**Fix**:
1. Add `ceil_flags=4194432` to the `f_valley` brush definition (line ~3786) — this is `PF_FakeBackdrop (4194304) | PF_Unlit (128)` which tells the engine to project the skybox through the ceiling.
2. Add a new `f_sky_opening` brush (matching the UE1 pattern at line ~1838) that subtracts a thin slab across the full ceiling to guarantee no opaque tiles remain.

---

### Component 2: Castle Grounding & Terrain Integration (Defect 2)

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py)

**Problem**: The castle bluff is an additive box that starts at `Z=-1024`, but its walls sit entirely within the subtracted valley void with no visual terrain ramps connecting it to surrounding ground level. From the 3D perspective view, the castle appears to hover.

**Fix**:
1. Add 2-3 **additive terrain shelf/ramp** brushes that slope from the canyon floor (`Z=-1024`) up to the bluff plateau, using cliff rock textures. These create the visual "mountain base" that the gold standard reference shows.
2. Add a **cliff face skirt** additive brush extending below and around the bluff to simulate the sheer granite rock face visible in the reference image.
3. Add **stepped rock terrace** semi-solid brushes along the bluff edge for visual richness.

---

### Component 3: Texture Validation & Fallback (Defect 3)

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py)

**Problem**: Texture references like `AntalusTextures.Terrain.Dirt1` may not match all UT2004 installs. The `OBJ LOAD` commands use `.utx` extensions.

**Fix**:
1. Validate texture package names against known UT2004 core packages. Use the standard UT2004 Megapack texture names.
2. Ensure the `OBJ LOAD` commands use correct relative paths (`..\\Textures\\PackageName.utx`).
3. Add the `HumanoidArchitecture` and `UCGeneric` packages as fallback texture sources — these ship with every UT2004 install.

---

### Component 4: River Gorge Safety (Defect 4)

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py)

**Problem**: The river gorge extends to the full valley length with no end caps. Players can walk or fall off the map edges.

**Fix**:
1. Shorten the river gorge Y dimension to `length - 512` (leaving 256 UU of solid rock at each end as natural end-caps).
2. Add **additive blocking volume** brushes at both Y extremes of the river to seal the gorge and prevent map-edge leaks.

---

### Component 5: Remove Purposeless Geometry (Defect 5)

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py)

**Problem**: Waterfall subtracted brushes positioned outside the main valley bounds create BSP holes and invisible collision walls.

**Fix**:
1. Verify all waterfall, corridor, and auxiliary brush positions are fully contained within the main valley subtract bounds (`±width/2`, `±length/2`).
2. Clamp the upper waterfall Y position from `-896` to a value within `(-length/2 + 384)`.
3. Ensure the waterfalls subtract *into* the cliff face brushes, not out into void space.

---

### Component 6: Semi-Solid Decorative Detail (Defect 7)

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py)

**Problem**: The UT2004 generator produces zero semi-solid decorative geometry. The UE1 version has 12+ types. This makes the UT2004 version look bare and unfinished.

**Fix**: Add the following semi-solid detail brushes (using `_write_semisolid_brush_file`):
1. **Rock terraces** along cliff edges for visual mass
2. **Castle merlons** along tower tops for crenellation silhouette
3. **Bridge stone piers** beneath the lower bridge for structural visual support
4. **Bridge arch ribs** — semi-solid arched understructure
5. **Waterfall sheets** — translucent water curtain panels (`PF_Translucent = 4`)
6. **River surface** — translucent water plane in the gorge

---

### Component 7: CSG Lesson Documentation

#### [MODIFY] [08_DEEP_HARDCORE_CRITICAL_ARCHITECTURE_AND_ENGINEERING_AUDIT.md](file:///d:/Projects/unrealagentharness/docs/08_DEEP_HARDCORE_CRITICAL_ARCHITECTURE_AND_ENGINEERING_AUDIT.md)

Add a new section documenting the geometry engineering anti-patterns discovered from the `agentharness_114.png` visual audit, specifically:
- **DO NOT** omit `FakeBackdrop|Unlit` flags on outdoor ceiling surfaces
- **DO NOT** place additive brushes floating in void without terrain ramps connecting them to ground
- **DO NOT** extend subtracted gorges/channels to the map edge without blocking end-caps
- **DO NOT** position subtracted brushes outside the main subtracted hull
- **DO NOT** ship generators without semi-solid decorative detail

---

### Component 8: Test Suite Expansion

#### [MODIFY] [test_harness.py](file:///d:/Projects/unrealagentharness/test_harness.py)

Add new test assertions for the UT2004 Valley Fortress generator:
1. **Skybox flag test**: Verify `ceil_flags=4194432` is passed to the main valley brush
2. **Sky opening brush test**: Verify `f_sky_opening` brush exists in the command list
3. **River bounds test**: Verify river gorge Y dimension is shorter than valley length
4. **Blocking volume test**: Verify gorge end-cap blocking brushes exist
5. **Semi-solid count test**: Verify minimum number of semi-solid detail brushes

---

## Verification Plan

### Automated Tests
```bash
cd d:\Projects\unrealagentharness
python -m pytest test_harness.py -v --tb=short 2>&1 | head -80
```

### Manual Verification
1. Run the UT2004 Valley Fortress generator via the Tkinter cockpit
2. Capture a new 4-viewport screenshot and compare against `agentharness_114.png`
3. Verify skybox renders correctly (no opaque grey ceiling)
4. Verify castle is visually grounded to terrain
5. Verify textures apply correctly
6. Verify river has end-caps (no map-edge leaks)

---

> [!IMPORTANT]
> This remediation brings the UT2004 Valley Fortress to parity with the UE1 version's engineering quality. The UE1 generator (`generate_ut99_verdant_mountain_valley`) was already correct in all these areas — the UT2004 version was built from a simplified template that omitted critical flags, grounding geometry, and decorative detail.

> [!WARNING]
> The texture package names (`AntalusTextures`, `AbaddonArchitecture`, `ArboreaArchitecture`) are from the standard UT2004 install. If you're using a custom UT2004 build or modded install, these packages may not be present. The fix adds fallback texture references from guaranteed-present core packages.
