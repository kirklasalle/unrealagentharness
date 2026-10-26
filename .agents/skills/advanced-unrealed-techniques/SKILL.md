---
name: advanced-unrealed-techniques
description: Advanced UnrealEd editing techniques, BSP tree optimization, semi-solid brushes, poly flags bitmasks, zone portals, WarpZones, skybox parallax, 2D shape editor, and brush clipping.
---

# Advanced UnrealEd Techniques & Methods Skill

## Overview

The **Advanced UnrealEd Techniques & Methods Skill** codifies 28 years of master-level UnrealEd secrets, BSP tree optimization techniques, non-Euclidean spatial tricks, and console command sequences across UnrealEd 1, 2, 3 (UT99/UT2004) and Unreal Engine 5. It guarantees maximum visual fidelity, rock-solid framerates, and zero BSP cuts within the **75% Engine Budget Law**.

```
                              [ ADVANCED UNREALED SUITE ]
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
       [ BSP & BRUSH TAXONOMY ]    [ POLY FLAGS BITMASKS ]     [ SPATIAL PORTALS ]
       • Solid (Cuts World)      • PF_FakeBackdrop (4194304) • Zone Portals (PF_Portal)
       • Subtractive (Carves)    • PF_Unlit (4194432)        • WarpZones (Non-Euclidean)
       • Semi-Solid (No Cuts)    • PF_Translucent (4)        • SkyZoneInfo Parallax (1:16)
                │                        │                        │
                └────────────────────────┼────────────────────────┘
                                         ▼
                            [ IN-EDITOR VECTOR TOOLS ]
                       • 2D Shape Editor (Revolve / Extrude)
                       • Brush 2D Planar Clipping & Splitting
                       • Intersect / De-intersect Boolean Carving
```

---

## 🏗️ Brush Taxonomy & BSP Tree Optimization

In Unreal's Binary Space Partitioning (BSP) compiler, every solid additive brush facet cuts across existing BSP leaf nodes, splitting polygons into smaller fragments. Unchecked solid brushes trigger the catastrophic **65k Node Limit General Protection Fault (GPF)** crash.

### 1. The 4 Brush Archetypes:
| Brush Type | CSG Operation | Flag Value | BSP Tree Impact | Golden Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Subtractive** | `CSG_Subtract` | `0` | Carves negative void out of infinite solid space | Master rooms, hallways, river gorges, moats |
| **Solid Additive** | `CSG_Add` | `0` | Cuts surrounding BSP nodes; solid collision | Structural bedrock, fortress curtain walls, floors |
| **Semi-Solid** | `CSG_Add` | `PF_Semisolid (32)` | **ZERO BSP cuts**; solid collision for players/weapons | Fluted pillars, arches, merlons, stairs, railings |
| **Non-Solid Sheet** | `CSG_Add` | `PF_NotSolid (8)` | **ZERO BSP cuts**; no player collision | Zone portals, waterfall sheets, god-rays, fire |

### The Golden Semi-Solid Rule
* **Rule**: Any architectural detail, fluted column, ceiling beam, buttress, or staircase placed *inside* an existing subtracted room MUST be constructed as a **Semi-Solid Brush (`PF_Semisolid = 32`)**.
* **Result**: Eliminates 80–90% of all BSP polygon cuts, preventing node tree inflation and eradicating BSP holes.

---

## 🚩 Master Poly Flags Bitmask Catalog

Every polygon facet in an Unreal T3D brush carries an integer `Flags` field encoding hardware rendering modes:

| Flag Name | Decimal Value | Hex Value | Visual & Engine Behavior |
| :--- | :--- | :--- | :--- |
| `PF_Invisible` | `1` | `0x00000001` | Polygon is completely invisible (used for collision-only boundaries). |
| `PF_Masked` | `2` | `0x00000002` | 1-bit alpha transparency (color index 0 is transparent; foliage, grates). |
| `PF_Translucent` | `4` | `0x00000004` | Additive blending transparency (waterfalls, energy shields, glass). |
| `PF_NotSolid` | `8` | `0x00000008` | Non-blocking ray-through surface (zone portals, fire planes). |
| `PF_Semisolid` | `32` | `0x00000020` | Solid collision with zero BSP node splits. |
| `PF_Modulated` | `64` | `0x00000040` | Multiplicative blending (shadow decals, smoke clouds, blast marks). |
| `PF_TwoSided` | `256` | `0x00000100` | Backface culling disabled; rendered from both front and rear. |
| `PF_FakeBackdrop` | `4194304` | `0x00400000` | Renders the isolated SkyZoneInfo camera vista instead of world texture. |
| `PF_Unlit` | `4194432` | `0x00400020` | Full self-illumination; immune to dynamic shadows and lightmaps. |
| `PF_Portal` | `67108864` | `0x04000000` | Zone portal sheet dividing rooms into independent BSP visibility zones. |
| `PF_Antiportal` | `134217728` | `0x08000000` | Dynamic occlusion volume hiding geometry behind it (UE2.5). |

---

## 🚪 Zone Portals & Room Occlusion Partitioning

Without zone portals, UnrealEd's engine renders every polygon in the entire map if a single ray can reach it.
* **Technique**: Seal doorway openings with a 2D sheet brush flagged with `PF_Portal | PF_NotSolid` (`Flags = 67108872`).
* **ZoneInfo Actor**: Place an `Engine.ZoneInfo` inside each room to control:
  * `bSoftKill`: Instant player obliteration outside bounds.
  * `ZoneGravity`: Low-gravity asteroid chambers (`ZoneGravity.Z = -300`).
  * `ZoneFluidFriction`: Water zones (`WaterZone`) and toxic sludge (`SlimeZone`).
  * `AmbientSound`: Audio reverberation presets (dungeon echo, cavern hall, metal room).

---

## 🌌 Isolated 1:16 Scale Parallax SkyBoxes

Outdoor ceilings must seamlessly project celestial horizons without rendering seams:
1. **Skybox Chamber**: Carve a small isolated subtractive box (`1024 x 1024 x 1024 UU`) far away from gameplay space (e.g., at coordinates `X=0, Y=0, Z=-8192`).
2. **SkyZoneInfo**: Spawn an `Engine.SkyZoneInfo` actor at the exact geometric center of the box.
3. **Parallax Ratio**: Objects placed inside the skybox chamber are scaled down 1:16 (a 64 UU mountain model represents a 1024 UU distant alpine peak).
4. **World Ceiling**: Flag outdoor ceiling polygons with:
   $$\text{Flags} = \text{PF\_FakeBackdrop } (4194304) \;|\; \text{PF\_Unlit } (4194432) = 4194432$$

---

## 🌀 WarpZones (Seamless Non-Euclidean Spatial Portals)

WarpZones connect two distant spatial openings so players, weapons fire, and camera views pass through continuously without loading screens:
* **Setup**: Place two matching 2D sheet portals tagged with `WarpZoneInfo`.
* **Properties**: Set `OtherSideActor = 'TargetWarpZoneMarker'` and matching coordinates.
* **Result**: Players looking through the doorway see the destination room with correct continuous perspective matrix raytracing.

---

## 📐 In-Editor Vector Tools

### 1. The 2D Shape Editor
* Open via `MODE 2DSHAPE` or toolbar icon.
* Draw vector contours with Bézier control points.
* **Revolve 360°**: Instantly generate fluted Doric/Corinthian column shafts and circular fountain basins.
* **Extrude Linear**: Generate custom cornice trim moldings and architrave profiles.

### 2. Brush Planar Clipping
* In any 2D viewport, toggle `MODE BRUSHCLIP`.
* Click two vertices to define a cutting plane. An arrow indicates the preserved half-space.
* Issue `BRUSH CLIP SPLIT` to divide a brush cleanly into two separate coplanar volumes without introducing vertex deformation.

### 3. Intersect & De-intersect Carving
* Position the red builder brush over existing geometry.
* **`BRUSH INTERSECT`**: Trims the builder brush to contain *only* the geometry shared with existing world geometry.
* **`BRUSH DEINTERSECT`**: Trims the builder brush to retain *only* what is inside the empty void.
