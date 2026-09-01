# Implementation Plan - World-Class Valley Fortress & Skybox Engine

Re-architect and elevate the Mountain Valley procedural world generator in **Unreal Agent Harness** to accurately synthesize the magnificent **Valley Fortress** visual target shown in the supplied reference image and replace the basic prototype shown in the supplied UnrealEd screenshot.

## Implementation status

**Current status: REQUIRES REWORK AND APPROVAL.** The generated map has not met runtime or visual acceptance: the supplied logs show a failed player spawn, invalid navigation fit, a collapsed bridge polygon warning, and a visible opaque tiled ceiling instead of the intended alpine skybox. The next work is governed by [`PROPOSAL_Valley_Fortress_Vision_UI_Reliability_Elevation.md`](PROPOSAL_Valley_Fortress_Vision_UI_Reliability_Elevation.md); the existing detail additions are not considered a faithful or playable final recreation.

The one-click UT99 palette entry **Valley Fortress — Image Fidelity (75% UE1)** now routes to the dedicated Valley Fortress compiler.  The implementation is additive and preserves the existing generic builders.  It now adds:

- a staged world-first build order with isolated skybox, canyon silhouette, grounded geology, fortress, bridges, details, actors, lighting, and final compilation;
- semi-solid stepped cliff terraces, crenellations, window surrounds, bridge piers, river surface, waterfall sheets, and stepping stones;
- a non-overlapping 52-node navigation lattice plus authored tree/fern clusters and warm fortress/cool river bounce lighting;
- regression tests proving the ultra-detail layers and standard-detail fallback remain distinct.

The 75% target is treated as a **budget policy**, not a claim that UE1 can reproduce modern high-resolution concept-art assets. UT99 uses BSP, stock actor meshes, texture packages, and semi-solid decorations; fidelity therefore comes from composition, silhouette, layering, texture selection, lighting contrast, and gameplay-readable landmarks rather than modern mesh density.

---

## 🎯 Architectural Breakdown (Matching `Builderbutton_valley_01.jpg`)

```
                                  [ SKYBOX CHAMBER ]
                             (Isolated at Z=+4608 with SkyZoneInfo)
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         [ WEST MOUNTAIN CLIFFS ]                          [ EAST FORTRESS BLUFF ]
       • Multi-Tier Rock Terraces                        • High Promontory Plateau
       • Waterfall Sheer Cliff Faces                     • Multi-Tower Stone Castle Keep
       • Peak Lookout Watchtowers                        • Fortified Gatehouse & Parapets
       • Dense Pine Tree Groves                          • Interior Castle Armory
                      │                                               │
                      └───────────────────────┬───────────────────────┘
                                              ▼
                                 [ CENTRAL RIVER GORGE ]
                               • Deep Chasm (-1024 UU Floor)
                               • Crystal River Water Bed (GenFluid)
                               • Lower Arched Stone Bridge
                               • Upper Timber Drawbridge
                               • Riverside Health Vials & Armor
```

---

## 🏗️ Technical Enhancements & Procedural Formulae

### 1. True Skybox System with Parallax `SkyZoneInfo`

- **Skybox Chamber**: Subtracted isolated `1024x1024x1024` room at `X=0, Y=0, Z=4608` textured with alpine sky (`ShaneSky.pansky1` / `GenFluid.pSky1`).
- **`Engine.SkyZoneInfo`**: Spawned at `(0, 0, 4608)` to broadcast celestial parallax views.
- **`FakeBackdrop` Flags (`Flags=128`)**: Applied to all top-facing ceiling surfaces of the main canyon world, projecting the distant sky.

### 2. Multi-Tier Canyon Chasm & Mountain Cliff Geometry

- **Main Valley Hull**: Deep `4608x4608x1792` canyon subtractive hull with rugged rock walls (`GenEarth.Rockfac1` / `Rock8` / `grasrok2`).
- **Deep River Chasm**: Central `896x4608x384` gorge carved along the valley floor.
- **Cliff Terraces & Rock Bluffs**: Stepped additive/subtractive rock shelves creating natural climbing terrain.
- **Waterfalls**: Vertical flowing water sheets (`GenFluid.Water1` / `water2`) cascading down the West mountain face into the river gorge below.

### 3. Grand Multi-Tower Castle Keep & Fortifications

- **High Promontory Citadel**: Additive `1280x1280x640` stone castle keep (`NaliCast.CasWAL` / `CasFLOR`).
- **Flanking Bastion Towers**: Four octagonal battle towers (`sides=8`, `OldWallH` / `CasWAL` / `ntrim2`) rising above the battlements.
- **Fortified Gatehouse & Arched Portal**: Massive entry portal with portcullis frame (`NaliCast.Casdoor2` / `Ancient.Arch`).
- **Inner Sanctum / Great Hall**: Subtracted interior armory chamber (`896x896x384`) with torches and weapon caches.

### 4. Dual Bridges Over the Gorge

- **Lower Grand Arched Stone Bridge**: Spans the lower river chasm with stone masonry arches and steps (`steps` / `CasWAL` / `METTRIM1`).
- **Upper Fortress Drawbridge**: Suspended timber bridge (`NaliCast.wood1` / `wood2` / `ShaneChurch.Bwood`) leading directly across the upper gorge to the castle gatehouse.

### 5. High Cliff & Peak Lookout Posts

- Timber and stone sniper watchtowers placed on West mountain peaks and East ridge overlooks.
- Accessible via mountain footpaths, equipped with Sniper Rifles and ammo crates.

### 6. World Foliage, Rocks, Medieval Torches & Botpack Lattice

- Authentic 3D pine trees (`UnrealShare.Tree1`, `Tree2`, `Tree3`, `Tree6`) clustered naturally across bluffs and ridges.
- Mountain shrubs and ferns (`Plant1`, `Plant2`, `Plant3`, `Plant5`, `Plant7`).
- Granite boulders (`UnrealI.BigRock`, `UnrealShare.Boulder`, `UnrealShare.SmallRock`) lining the riverbed and cliffs.
- Medieval torch sconces (`UnrealShare.TorchFlame`) illuminating gatehouses and bridge abutments.
- Full 24-node Botpack AI reachability graph covering river gorge, bridges, castle interior, and sniper lookouts.

---

## 📁 Proposed Changes

| Component | File | Action | Purpose |
| :--- | :--- | :--- | :--- |
| **Formula Engine** | [`G:\UnrealTournament\AgentHarness\core\formula_engine.py`](file:///G:/UnrealTournament/AgentHarness/core/formula_engine.py) | **MODIFY** | Upgrade `_generate_brush_polylist_t3d` for `ceil_flags=128` and completely rewrite `generate_ut99_verdant_mountain_valley` to synthesize the complete Valley Fortress world |
| **Unit Tests** | [`G:\UnrealTournament\AgentHarness\test_harness.py`](file:///G:/UnrealTournament/AgentHarness/test_harness.py) | **MODIFY** | Verify all CSG brush definitions, T3D poly lists, and actor allocations |
| **Documentation** | [`G:\UnrealTournament\AgentHarness\CHANGELOG.md`](file:///G:/UnrealTournament/AgentHarness/CHANGELOG.md) | **MODIFY** | Document v2.7.0 Valley Fortress engine upgrade |

---

## 🧪 Verification Plan

### Automated Verification

- Run `pytest test_harness.py` or `python test_harness.py` to ensure all tests pass cleanly without errors.

### Manual / In-Editor Verification

- Trigger the **🏔️ Verdant Mountain Valley** builder button in the Harness Cockpit.
- Verify in UnrealEd viewports:
  1. True skybox chamber with `SkyZoneInfo` rendering through `FakeBackdrop` sky surfaces.
  2. Multi-tower stone castle keep with gatehouse and interior.
  3. Dual bridges (lower stone arch bridge & upper wooden drawbridge).
  4. Deep river gorge with flowing water and waterfall sheets.
  5. Mountain peak watchtowers, pine forest clusters, torches, and Botpack AI navigation network.
