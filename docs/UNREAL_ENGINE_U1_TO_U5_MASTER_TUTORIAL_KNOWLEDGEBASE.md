# Unreal Engine Master Tutorial Knowledge Base (U1 to U5)

---

## Executive Overview

The **Unreal Engine Master Knowledge Base** is an authoritative reference architecture, procedural level design compendium, and engineering manual covering all five generations of Epic Games' Unreal technology (UE1 through UE5). It codifies core rendering philosophies, CSG BSP algorithms, static mesh pipelines, lighting physics, bot path lattice mathematics, vehicle kinematics, creature AI, and UnrealEd automation directives.

---

## 1. Unreal Engine Evolutionary Timeline & Architectural Matrix

| Metric | Unreal Engine 1 (UE1) | Unreal Engine 2 / 2.5 (UE2.5) | Unreal Engine 3 (UE3) | Unreal Engine 4 (UE4) | Unreal Engine 5 (UE5) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Flagship Titles** | Unreal (1998), UT99 GOTY, Deus Ex, ChaosUT, Tactical Ops | UT2004, UT2003, Postal 2, SWAT 4 | UT3, Gears of War, Bioshock | UT4, Fortnite, Robo Recall | Fortnite Chapter 4+, Matrix Awakens |
| **Geometry Core** | Pure CSG BSP (Subtractive) | Hybrid CSG + Static Meshes (.usx) | Dominant Static Meshes + Modular CSG | Full Modular Static Meshes + Volumes | Nanite Virtualized Micro-Polygons |
| **Physics Engine** | Native Tick-based Physics (PHYS_Falling, PHYS_Walking) | Karma Physics Engine (MathEngine) + SVehicles | PhysX 2.x / 3.x Rigid Body Physics | PhysX / Chaos Physics | Chaos Physics & Chaos Destruction |
| **Scripting / Logic** | UnrealScript (Bytecode VM, .u packages) | UnrealScript v2 (State machines, dynamic arrays) | UnrealScript + Kismet Visual Scripting | C++ & Blueprint Visual Scripting | C++ & Enhanced Blueprints + Verse |
| **Global Illumination**| Precomputed Raytraced Lightmaps | Precomputed Vertex/Lightmaps + ZoneLight | Lightmass Global Illumination | Lightmass + DFAO / Distance Fields | Lumen Real-Time Dynamic GI & Reflections |
| **Bot / AI Pathing** | PathNode Lattice Graph & ReachSpecs | PathNode + RoadPathNode + FlyingPathNode | Pylon-based NavMesh Generation | Recast / Detour Dynamic NavMesh | Recast NavMesh + Mass Entity + StateTree |
| **Coordinate Scale** | 1 Unreal Unit (UU) = 0.75 inches (~16 UU = 1 foot) | 1 UU = 0.75 inches (~50 UU = 1 meter) | 1 UU = 1 cm (Standard Metric) | 1 UU = 1 cm (Standard Metric) | 1 UU = 1 cm (Standard Metric) |

---

## 2. CSG (Constructive Solid Geometry) & World Foundations

### 2.1 The Subtractive vs. Additive Paradigm
- **Subtractive Space (UE1 & UE2.5)**:
  - The default universe is a solid, infinitely dense mass of rock/matter.
  - Level architects **carve voids** out of the void using the **Red Builder Brush** with `BRUSH SUBTRACT`.
  - Additive brushes (`BRUSH ADD`) are then placed *inside* subtracted rooms to create pillars, walkways, platforms, and dais structures.
- **Additive Space (UE3, UE4 & UE5)**:
  - The default universe is an infinite empty vacuum.
  - Level architects build positive geometry (Static Meshes, Landscapes) into empty space.

### 2.2 T3D PolyList Polygon Grammar
UnrealEd utilizes the text-based `.t3d` (Unreal 3D Text) standard to exchange brush geometry and actor hierarchies:

```t3d
Begin PolyList
   Begin Polygon Item=Floor Texture=AntalusTextures.Terrain.Dirt1 Flags=0
      Origin   -1536.000000,-1536.000000,-512.000000
      Normal   +0.000000,+0.000000,+1.000000
      TextureU +1.000000,+0.000000,+0.000000
      TextureV +0.000000,+1.000000,+0.000000
      Vertex   -1536.000000,+1536.000000,-512.000000
      Vertex   +1536.000000,+1536.000000,-512.000000
      Vertex   +1536.000000,-1536.000000,-512.000000
      Vertex   -1536.000000,-1536.000000,-512.000000
   End Polygon
End PolyList
```

#### Critical Rules for PolyList Geometry:
1. **Clockwise Winding**: Vertex order must follow right-hand clockwise winding relative to the surface outward Normal vector.
2. **Coplanar Planarity**: All vertices of a polygon must strictly reside on the exact same mathematical plane ($Ax + By + Cz + D = 0$). Non-coplanar quads cause BSP hole corruption.
3. **Watertight Topology**: Every brush must be 100% closed with zero unshared edges.

---

## 3. Lighting Science & Atmosphere Engineering

### 3.1 Unreal Color Model (Hue / Saturation / Brightness)
In UE1 and UE2.5, lighting utilizes an 8-bit HSV color system:
- **`LightBrightness` (0–255)**: Intensity multiplier. Standard room lights range from 120 to 220; sunlight ranges from 240 to 255.
- **`LightRadius` (0–255)**: Radial attenuation boundary. $Radius \approx LightRadius \times 64\text{ UU}$.
- **`LightHue` (0–255)**: 360-degree color wheel mapped to 256 steps:
  - `0`: Fiery Red
  - `25`: Torchfire Orange
  - `35`: Sunlit Gold / Amber
  - `85`: Emerald Skaarj Green
  - `145`: Electric Cyan
  - `170`: Plasma Blue
  - `210`: Neon Violet / Magenta
- **`LightSaturation` (0–255)**: Inverted saturation: `0` represents pure vivid color saturation, while `255` represents pure monochrome white light.

### 3.2 Special Animation Light Types
- **`LT_None`**: Static illumination.
- **`LT_Pulse`**: Smooth sinusoidal breathing pulse (ideal for reactor cores and power nodes).
- **`LT_Blink` / `LT_Flicker`**: Irregular electrical short or torchlight flicker.
- **`LT_Strobe`**: Fast, sharp on/off cycle (ideal for emergency alarms and bio-hazard quarantine).
- **`LT_SubtlePulse`**: Gentle ambient breathing for high-tech holographic consoles.

---

## 4. Vehicle Physics, Kinematics & Onslaught Networking (UE2.5)

### 4.1 Onslaught Vehicle Hierarchy
In UT2004, vehicles inherit from `Engine.SVehicle` (Super Vehicle) through `Onslaught.ONSVehicle`:

```
Actor
 └── Pawn
      └── Vehicle
           └── SVehicle (Karma physics rigid body)
                ├── ONSVehicle (Onslaught combat vehicle base)
                │    ├── ONSWheeledCraft (ONSRV Scorpion, ONSPRV Hellbender, Paladin)
                │    ├── ONSHoverCraft (ONSHoverBike Manta, ONSHoverTank Goliath)
                │    ├── ONSChopperCraft (ONSAttackCraft Raptor, ONSBomber Cicada)
                │    └── ONSMobileAssaultStation (Leviathan 5-man fortress)
                └── ASTurret (Assault defense emplacements)
```

### 4.2 Handling & Kinematic Parameters
- **Hovercraft Dynamics (`ONSHoverCraft`)**:
  - `ThrusterOffsets`: Local vectors defining repulsive cushions off terrain.
  - `HoverCheckDist`: Raycast down distance for cushion calculation (typically 90–140 UU).
  - `MaxThrustForce` & `MaxSteerTorque`: Angular turning and acceleration power.
- **Wheeled Dynamics (`ONSWheeledCraft`)**:
  - `WheelSuspensionTravel`: Vertical spring displacement.
  - `TireRollFriction` & `TireLateralFriction`: Longitudinal and lateral grip coefficients.
  - `HandbrakeFrictionFactor`: Allows drift maneuvers in the Scorpion.

---

## 5. Bot AI Navigation Lattice & Pathing Mathematics

### 5.1 The ReachSpec Navigation Graph
Unreal Engine bots navigate via a directed graph composed of **Nodes** (`Engine.PathNode`, `Engine.PlayerStart`, `Engine.InventorySpot`, `XGame.xJumpPad`) and **Edges** (`ReachSpecs`):

$$\text{ReachSpec} = \{\text{StartNode}, \text{EndNode}, \text{CollisionRadius}, \text{CollisionHeight}, \text{ReachFlags}\}$$

#### Essential Pathing Rules:
1. **Maximum Node Distance**: Standard ground infantry path nodes should be spaced **400 to 700 UU** apart. Distances $> 1000\text{ UU}$ break reachability.
2. **Clear Line of Sight**: PathNodes must have unobstructed line of sight with adequate player bounding box clearance ($CollisionRadius \ge 40\text{ UU}, CollisionHeight \ge 80\text{ UU}$).
3. **Z-Floor Elevation**: Place nodes **20 to 35 UU above floor geometry** to prevent physics floor penetration.
4. **Specialized Nodes**:
   - `Engine.RoadPathNode`: Used for wide vehicle roads ($Radius \ge 150\text{ UU}$).
   - `Engine.FlyingPathNode`: 3D aerial waypoints for Raptors and Cicadas ($Z \approx 500\text{--}1200\text{ UU}$).
   - `XGame.xJumpPad`: Ballistic velocity launcher paired with landing target.

---

## 6. SkaarjPack & Invasion Creature AI (UE2.5)

### 6.1 Creature Class Roster
The `SkaarjPack.u` engine package powers UT2004 Invasion mode and custom single-player adventures:

- **`SkaarjPack.Skaarj`**: Agile bipedal warrior with wrist blades, energy projectiles, and sidestep dodging.
- **`SkaarjPack.WarLord`**: Flying boss capable of sustained aerial hover, homing rockets, and ground divebombs.
- **`SkaarjPack.Titan`**: Colossal 800-HP prehistoric beast that rips boulders from the terrain and hurls them with devastating splash damage.
- **`SkaarjPack.Krall` / `KrallElite`**: Alien shock troops armed with concussive energy staves.
- **`SkaarjPack.Brute` / `Behemoth`**: Heavy bio-armored tanks with dual arm rocket launchers.
- **`SkaarjPack.Pupae`**: Lightning-fast ceiling and wall-crawling insectoid swarmers.
- **`SkaarjPack.Fly` (Razorfly)**: Buzzing winged pests that divebomb player heads.
- **`SkaarjPack.Gasbag`**: Floating gaseous levitators that vomit explosive plasma globules.

---

## 7. Master Console Command Automation Reference

| Automation Objective | UnrealEd Command (UE1 / UE2.5) | Modern Engine Equivalent (UE4 / UE5) |
| :--- | :--- | :--- |
| **New Level Template** | `MAP NEW` | `File -> New Level` |
| **Import CSG Brush** | `BRUSH IMPORT FILE="<file.t3d>"` | `Import -> Static Mesh` |
| **Subtract CSG Brush** | `BRUSH SUBTRACT` | Geometry Script / Modeling Mode |
| **Add CSG Brush** | `BRUSH ADD` | Geometry Script / Modeling Mode |
| **Move Builder Brush** | `BRUSH MOVETO X=<x> Y=<y> Z=<z>` | `SetActorLocation` |
| **Spawn Typed Actor** | `ACTOR ADD CLASS=<package.class>` | `SpawnActorOfClass` |
| **Import Actor Map** | `MAP IMPORT FILE="<file.t3d>"` | `LoadMap / Level Streaming` |
| **Full Level Rebuild** | `MAP REBUILD` | `Build All Levels` |
| **Apply Lighting** | `LIGHT APPLY` | `Build Lighting (Lightmass)` / Lumen Auto |
| **Build Path Network**| `PATHS BUILD` | `Build Paths / Navigation Mesh` |
| **Flush Texture Cache**| `FLUSH` | `r.TextureStreaming 0 / Flush` |
| **Duplicate Actor** | `ACTOR DUPLICATE` | `Alt + Drag / Duplicate` |
| **Delete Actor** | `ACTOR DELETE` | `DestroyActor` |

---

## 8. Generation Transition Guide (From UE1/2 to UE5)

1. **CSG to Nanite Virtualization**:
   - In UE1/UE2, polycount conservation was paramount ($< 50,000$ polygons per frame).
   - In UE5, Nanite processes millions of polygons with continuous LOD streaming and virtual shadow maps.
2. **Precomputed Lights to Lumen Real-Time GI**:
   - In UE1/UE2, lighting was baked into static surface lightmaps.
   - In UE5, Lumen provides dynamic real-time diffuse inter-reflections, emissive surface bounces, and infinite sky specular reflections.
3. **ReachSpecs to Mass Entity NavMesh**:
   - In UE1/UE2, discrete PathNodes with ReachSpecs formed the AI graph.
   - In UE5, continuous Recast NavMesh volumes paired with Mass Entity ECS provide crowd simulation for thousands of concurrent agents.
