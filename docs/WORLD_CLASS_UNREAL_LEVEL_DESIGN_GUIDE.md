# World-Class Unreal Level Design & Architecture Guide

### Comprehensive Knowledge Base: UE1 (UT99), UE2.5 (UT2004), and UE5.x

**Author:** Kirk LaSalle & Antigravity AI Architect  
**Version:** v2.6.0  
**Target Engines:** Unreal Tournament 99 GOTY (UE1/469e), UTron TC, UT2004 (UE2.5), Unreal Engine 5.x

---

## 🏛️ 1. Unreal Tournament 99 (Unreal Engine 1 / OldUnreal 469e)

### A. BSP Geometry & Watertight Brush Construction

1. **Always Work on the Power-of-Two Grid**: Grid snapping (16, 32, 64, 128, 256) is mandatory. Freehand brush movement is the primary source of coplanar micro-gaps, polygon tearing, and catastrophic BSP holes.
2. **Semisolid vs. Solid Brushes**:
   - Use **Solids** strictly for the structural hull (walls, floors, ceilings, portals) that define visibility and zone boundaries.
   - Use **Semisolids** (`Add Special` -> `Semisolid`) for freestanding architectural decorations, pillars, stair steps, beams, and decorative trim. Semisolids do not cut the BSP tree, drastically reducing polygon counts and eliminating node bleeding.
   - Use **Non-Solids** for skybox geometry and water sheets.
3. **Preventing Non-Planar Polygons**: Every 3D brush face in `.t3d` PolyLists must be mathematically coplanar. If a vertex is sheared or transformed non-planarly, the BSP compiler will produce invisible surfaces or geometry crashes (`BspValidateBrush`).

### B. Zoning & Environmental Physics

1. **Zone Portals**: Sheet brushes placed across doorways and choke points, added via `Add Special -> Zone Portal`.
2. **Airtight Zoning**: A zone must be 100% sealed. If even a 1-unit gap exists, the zone will "leak" into adjacent chambers, causing zone overflow and ruining occlusion.
3. **Environmental Zone Effects**:
   - **Water Zones**: `ZoneInfo` with `bWaterZone=True`, `ZoneVelocity`, `ZoneFluidFriction`, and splash sounds.
   - **Low-Gravity / Space Zones**: `ZoneGravity=(Z=-350)` for authentic moonbase or low-g combat.
   - **Damage Zones**: `ZoneDamagePerSec`, `DamageType` (e.g. `Fell`, `Drowned`, `Burned`).

### C. Dynamic Lighting & Radiosity

1. **Key & Fill Lighting Ratios**:
   - Key Light: Brightness 220–250, Radius 80–128, warm sun/amber tones (`Hue=32`, `Sat=160`).
   - Ambient Fill Light: Brightness 160–180, Radius 64–96, complementary cool tones (`Hue=150`, `Sat=180`).
2. **Atmospheric Effects**:
   - `LightEffect = LE_TorchWaver` or `LE_FireWaver` for dynamic torch flickering.
   - `LightEffect = LE_WateryShimmer` for pool and river reflections.
   - Non-zero ambient brightness in `ZoneInfo` (`AmbientBrightness = 40–55`) prevents completely unlit black shadows.

### D. Texture Alignment, Scaling & Shading

1. **In-Memory Loading**: Always preload packages via `OBJ LOAD FILE="..\Textures\<Pkg>.utx" PACKAGE=<Pkg>` prior to brush imports.
2. **Texture Scale**:
   - Standard indoor walls and floors: `SCALE 1.0`.
   - Massive outdoor canyon cliffs and mountains: `SCALE 2.0` or `SCALE 4.0` with `PAN` adjustments to avoid tiling repetition.
3. **Surface Flags**:
   - `Unlit`: Glowing computer monitors, light fixtures, laser grids.
   - `Two-Sided`: Grates, railings, chainlink fences, plant sheets.
   - `Masked`: Foliage, grates, ladders (using palette index 0 as transparency).
   - `FakeBackdrop`: Applied to outdoor sky surfaces to project the external `SkyZoneInfo` parallax skybox.

### E. Botpack AI Navigation Lattice

1. **Spacing**: Keep `PathNodes` spaced 300 to 600 Unreal Units apart with direct line-of-sight.
2. **Elevation & Clearance**: Always elevate `PathNodes` and `PlayerStarts` +50 UU above the floor surface to guarantee the bot's collision cylinder (`CollisionHeight = 39`) clears floor polygon normals.
3. **Specialized Movement**:
   - `JumpSpot`: Used for ledges, jump pads, and boots. Always set `bAlwaysAccel=True`.
   - `LiftCenter` & `LiftExit`: Paired around elevator platforms to guide bot boarding and disembarking.

### F. Edge-Driven Macro Blockout and Playability Gates

1. **Measure before detail**: Convert reference-image edges and landmarks into normalized regions for west cliff, east fortress, river axis, upper bridge, lower bridge, waterfall, horizon, and foreground framing.
2. **Blockout first**: Build only the large grounded masses and one safe route. Capture perspective, top, front, and side views and compare against the scene graph before adding semisolids or foliage.
3. **Validate starts physically**: A `PlayerStart` must be supported by a walkable surface, clear of all structural/decorative collision, separated from other starts and path nodes, and confirmed by a real runtime spawn.
4. **Treat warnings as failures**: `FPoly::Fix: Collapsed a point`, `Scout didn't fit`, and `No valid start found` must block the detail pass and playtest certification.
5. **Preserve evidence**: Store the reference hash, annotation mask, scene graph, generated assets, editor log findings, screenshots, and repair decisions in the build manifest and durable graph memory.

---

## ⚡ 2. Unreal Tournament 2004 (Unreal Engine 2.5 / UnrealEd 3)

### A. Static Mesh Architecture & Occlusion

1. **BSP as Hull, Static Meshes as Detail**: Use simple additive/subtractive BSP boxes for primary level boundaries, and decorate with pre-compiled `.usx` static meshes.
2. **Antiportals**:
   - Place `AntiPortalActor` brushes inside large interior walls, pillars, and mountain peaks.
   - The engine occludes static meshes behind antiportal bounding boxes, drastically reducing draw calls.
3. **CullDistance & Detail Meshes**: Set `CullDistance` on small props (pebbles, pipes, grass blades) so they automatically fade out at long distances.

### B. Shaders & Material Systems

1. **Multi-Layer Shaders**: Combine `Diffuse`, `Specular`, `SpecularMask`, `SelfIllumination`, and `Normal/Bump` channels in `Engine.Shader`.
2. **FluidSurfaces**: Use `FluidSurfaceInfo` for interactive rippling water, tuned with `FluidGridSpacing` and `FluidNoise`.

### C. Onslaught & Karma Physics

1. **PowerNode Links**: Establish bidirectional links between `ONSPowerCore` and `ONSPowerNode` actors with `LinkHealMultipliers`.
2. **Vehicle Navigation**: Use `VehiclePathNode` and wide `RoadPathNodes` with large clearance radii to allow Mantas, Goliaths, and Raptors to navigate terrain without getting snagged.

---

## 🌌 3. Unreal Engine 5.x (Modern Architecture)

### A. Nanite & Lumen Best Practices

1. **Nanite Virtualized Geometry**:
   - Enable Nanite on high-poly meshes, rock formations, and architectural structures.
   - Avoid Nanite on thin translucent foliage or deformed skeletal meshes.
2. **Lumen Global Illumination**:
   - Use dynamic mesh distance fields for accurate software raytraced bounces.
   - Treat emissive materials as light sources, supplemented by local `PointLight` fill actors for low-spec fallback.

### B. World Partition & PCG (Procedural Content Generation)

1. **World Partition Grids**: Replaces legacy sub-levels with a runtime spatial streaming grid. Enable Data Layers to selectively stream gameplay elements.
2. **PCG Graphs**: Construct procedural splines and volume graphs to scatter trees, rocks, and foliage dynamically based on slope, height, and terrain material masks.

### C. Python Remote Execution (Port 30010)

- Automate level creation, asset placement, and property batching via the `unreal.EditorLevelLibrary` and `unreal.AssetTools` Python APIs.
