# UnrealEd 2.0 / 2.2 Skybox & Exterior World Master Guide

### Deep Technical Reference: Real-Time Parallax Skyboxes & Grounded Outdoor CSG Geometry

**Author:** Kirk LaSalle & Antigravity AI Architect  
**Engine Version:** Unreal Tournament 99 GOTY (UE1 / OldUnreal 469e / UnrealEd 2.2)  
**Target Runtimes:** UT99 GOTY, UTron TC, UT2003, UT2004, UE5.x

---

## 🌌 1. The Anatomy of an Unreal Tournament 99 Skybox

In Unreal Engine 1 / UnrealEd 2.2, outdoor environments do not have open-air "world bounds." Every map is constructed within a subtractive space. To create the illusion of an infinite, majestic celestial sky (as seen in `CTF-Face`, `DM-Peak`, `DM-Cybrosis`, and `Vortex Rikers`), UnrealEd uses a **virtual camera projection system**:

```
 ┌──────────────────────────────────────────────────┐
 │           ISOLATED SKYBOX CHAMBER                │
 │         (e.g., at X=-8192, Y=-8192, Z=4096)      │
 │                                                  │
 │   ┌──────────────────────────────────────────┐   │
 │   │  [SkyBox Texture: ShaneSky / GenEarth]  │   │
 │   │                                          │   │
 │   │                 ▲                        │   │
 │   │                 │                        │   │
 │   │          [SkyZoneInfo] ◄─ Camera Origin │   │
 │   │                 │                        │   │
 │   │                 ▼                        │   │
 │   │      [Sunlight / Rotating Clouds]        │   │
 │   └──────────────────────────────────────────┘   │
 └─────────────────────────┬────────────────────────┘
                           │ 
       Virtual Projection Vector (Parallax Tracking)
                           │
                           ▼
 ┌──────────────────────────────────────────────────┐
 │            PLAYABLE CANYON MAP                   │
 │                                                  │
 │   ╔══════════════════════════════════════════╗   │
 │   ║  CEILING / SKY SHEET:                    ║   │
 │   ║  Flags = 4194432 (FakeBackdrop | Unlit)  ║   │
 │   ║  (Engine renders SkyZoneInfo here)       ║   │
 │   ╚══════════════════════════════════════════╝   │
 │                       │                          │
 │         [Mountain Cliffs & Waterfall]            │
 │         [Grounded Castle Citadel]                │
 │         [River Gorge & Stone Bridges]            │
 └──────────────────────────────────────────────────┘
```

---

## 🛠️ 2. Step-by-Step Technical Rules for Flawless Skyboxes

### Rule 1: Extreme Isolation

* **Coordinate Placement**: Always place the Skybox chamber at an isolated location far outside the playable level bounding box (e.g., `X=-8192, Y=-8192, Z=4096`).
* **Preventing Light Bleed**: Never build the skybox immediately adjacent to the main canyon ceiling. A separation of at least $4000+$ Unreal Units ensures that local map dynamic lights (torches, rockets, muzzle flashes) never illuminate skybox walls, and skybox sun lights never cause irregular shadow leaks in the level.

### Rule 2: Precision `SkyZoneInfo` Centering

* The `Engine.SkyZoneInfo` actor MUST be placed at the **exact geometric center** of the Skybox room.
* If the `SkyZoneInfo` is even slightly off-center, the sky perspective will look warped or skewed when the player rotates their view in the canyon.

### Rule 3: Mandatory Dual Surface Flags (`FakeBackdrop | Unlit`)

* Every ceiling polygon and sky opening in the playable canyon level must be flagged with **BOTH**:
    1. `PF_FakeBackdrop = 0x00000080` (128): Tells the renderer to project the `SkyZoneInfo` view onto this surface.
    2. `PF_Unlit = 0x00400000` (4194304): Prevents local point lights and torch flames from casting dark blotchy shadows across the sky surface.
* **Combined PolyFlags**: `Flags = 4194432` (`128 | 4194304`).

### Rule 4: Skybox Interior Illumination

* Skybox interior wall surfaces must either be flagged as `Unlit` or illuminated with a central pure-white ambient light (`LightBrightness=255, LightHue=0, LightSaturation=0`) to ensure the sky textures glow with natural celestial radiance.

### Rule 5: Runtime Acceptance, Not Actor Presence

An imported `SkyZoneInfo` and a `Flags=4194432` polygon do not prove that the player sees a skybox. After `MAP REBUILD` and `LIGHT APPLY`, capture the playable perspective view and verify that the visible upper opening contains the intended sky gradient/cloud field rather than an opaque repeated material. Also verify that the level currently open in UnrealEd is the newly saved build, not a stale map.

### Rule 6: Reference-Driven Sky and Horizon Composition

When recreating a concept image, first extract the horizon band, cloud mass, distant mountain wedge, and annotated skybox region in normalized image coordinates. Build these as a separate skybox composition before adding foreground architecture. Red operator circles/lines are metadata and must be masked from edge extraction; they must never become sky geometry.

### Rule 7: Skybox Failure Diagnostics

If the captured view shows a flat tiled ceiling, check in order: active map identity, visible surface flags, sky texture/package resolution, `SkyZoneInfo` zone placement, chamber isolation, and camera route. Record the failing screenshot and log evidence in the build manifest before attempting a targeted repair.

---

## 🏰 3. Grounded Outdoor CSG Architecture (Eliminating Floating Geometry)

To ensure structures look authentic and monumental like the reference art in [Builderbutton_valley_01.jpg](file:///g:/UnrealTournament/docs/Builderbutton_valley_01.jpg):

1. **Solid Foundation Plateaus**:
    * Any fortress, castle keep, or watchtower built on high ground must have a **continuous masonry/rock foundation block** that extends all the way down to $Z = floor\_z$ (the valley floor).
    * No structure should ever hover mid-air without structural cliff buttresses or solid stone foundations beneath it.
2. **Integrated Bridge Abutments**:
    * Bridges spanning the river gorge must feature deep masonry piers that plunge into the riverbed rock, with approach ramps keyed directly into the canyon trail coordinates.
3. **Tiered Mountain Cliffs & Waterfalls**:
    * Cliffs are constructed with stepped subtractive and additive rock shelves (`GenEarth.Rockfac1` / `Rock8`), with vertical recessed waterfall chasms (`GenFluid.water2` / `Water1`) cascading directly into the river below.
