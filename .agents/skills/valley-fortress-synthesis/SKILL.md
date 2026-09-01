---
name: valley-fortress-synthesis
description: Comprehensive level design and CSG synthesis skill for generating the world-class Valley Fortress outdoor world in Unreal Engine 1 / UT99, matching reference Builderbutton_valley_01.jpg.
---

# Valley Fortress World Synthesis Skill

## Overview

The **Valley Fortress World Synthesis Skill** proceduralizes the majestic mountain valley and fortified castle depicted in `Builderbutton_valley_01.jpg` for Unreal Tournament 99 / OldUnreal 469e, fully adhering to the 75% engine budget policy, watertight CSG principles, and perspective edge-alignment.

```
                                  [ SKY DOME / ALPINES ]
                              (High clouds, distant peaks)
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       [ WEST CLIFFS & WATERFALLS ]                    [ EAST CASTLE BLUFF ]
     • Steep granite rock terraces                   • Sheer vertical granite cliff
     • Upper deep ravine waterfall                   • Majestic multi-tower castle keep
     • Lower foreground waterfall                    • 4 Octagonal bastion towers
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

---

## Architectural & CSG Breakdown (Matching `Builderbutton_valley_01.jpg`)

### 1. Starting Position & Viewport Centering Commands
When preparing or inspecting the Valley Fortress in UnrealEd, the standard 5-command execution order is:
1. **Command 1 (Vantage Position)**: Move camera to foreground vantage point overlooking the valley:
   ```text
   CAMERA MOVETO X=-600 Y=1400 Z=400 PITCH=-3000 YAW=-16000 ROLL=0
   ```
2. **Command 2 (Top View Center & Zoom)**:
   ```text
   VIEWPORT TOP ZOOM=100
   ```
3. **Command 3 (Front View Center & Zoom)**:
   ```text
   VIEWPORT FRONT ZOOM=100
   ```
4. **Command 4 (Side View Center & Zoom)**:
   ```text
   VIEWPORT SIDE ZOOM=100
   ```
5. **Command 5 (Dynamic Lighting & Redraw)**:
   ```text
   MODE DYNAMICLIGHT
   CAMERA ALIGN
   VIEWPORT REDRAW
   ```

---

### 2. Parallax Skybox Chamber
* **Chamber**: Subtracted $1024 \times 1024 \times 1024$ cube at $(0, 0, 4608)$ isolated from the main play space.
* **Actor**: `Engine.SkyZoneInfo` spawned at $(0, 0, 4608)$.
* **Textures**: Alpine sky textures (`ShaneSky.DaySky1` / `GenFluid.pSky1`).
* **Projection**: All upper ceiling surfaces of the main valley canyon are flagged with `FakeBackdrop` (`Flags=4194432` / `PF_FakeBackdrop | PF_Unlit`), projecting the celestial sky dome across the entire horizon.

---

### 3. East Granite Bluff & Castle Fortress (The Red Circle in Reference)
* **Sheer Granite Bluff**: Massive sheer rock promontory on the right side ($X = 896 \text{ to } 2304$) rising from river gorge depth ($Z = -896$) up to plateau elevation ($Z = +256$) textured with natural granite bedrock (`GenEarth.Rockfac1`, `Rock8`, `grasrok2`).
* **Castle Keep & Bastions**: Perched directly atop the sheer rock cliff ($Z = +256 \text{ to } +1408$):
  - Additive stone masonry keep ($1408 \times 1408 \times 512$) textured with `NaliCast.CasWAL` and `CasFLOR`.
  - 4 Octagonal battle towers with parapet level and conical spires.
  - Fortified arched gatehouse portal (`Ancient.Arch`, `Casdoor2`).
  - Interior Great Hall armory sanctum with torches and weapons.

---

### 4. Dual Waterfalls (Exact Reference Placement)
* **Waterfall 1 (Upper Deep Ravine)**: Located in the mid-ground left mountain cleft ($X = -1792, Y = -896$), cascading from mountain shelf ($Z = +512$) down into the river gorge with translucent sheets (`GenFluid.Water1`) and `WaterfallGlowUpper` shimmer light.
* **Waterfall 2 (Lower Foreground Cliff)**: Located on the left foreground cliff face ($X = -1280, Y = +768$) plunging down into the river gorge beside the Lower Stone Bridge with `WaterfallGlowLower` shimmer light.

---

### 5. Dual Bridges Over the Gorge
* **Lower Grand Arched Stone Bridge**: Masonry bridge spanning the foreground chasm ($Y = +768$) with a wide stone arch rib and approach steps (`NaliCast.CasWAL`, `METTRIM1`).
* **Upper Timber Drawbridge**: Suspended wooden bridge ($Y = 0$) connecting the west mountain trail directly across the deep abyss into the elevated castle gatehouse.

---

### 6. West Mountain Watchtowers & Foliage
* **Lookout Posts**: Timber sniper watchtowers perched on high West cliff pinnacles.
* **Foliage**: Clustered 3D pine trees (`UnrealShare.Tree1-6`) across ridges and shrubs (`Plant1-7`) along river banks.
* **Lighting**: Warm torch sconces (`TorchFlame`) on castle and bridge contrasting against cool alpine blue sky and river bounce lighting.
