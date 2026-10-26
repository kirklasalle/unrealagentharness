---
name: unreal-3d-and-animation
description: World-class 3D development, CSG/BSP mathematical geometry, vertex and skeletal mesh animation, collision hulls, Karma physics dynamics, and cinematic Matinee sequencing.
---

# Unreal 3D Development & Animation Skill

## Overview

The **Unreal 3D Development & Animation Skill** provides master-level mathematical, geometric, and cinematic techniques for Unreal Engine level design across UE1, UE2.5, and UE5. It governs the entire 3D spatial pipeline from mathematical plane equations and binary space partitioning (BSP) trees to skeletal deformation, collision hulls, rigid body dynamics, and cinematic choreography.

```
                              [ 3D SPATIAL PIPELINE ]
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
       [ CSG & BSP GEOMETRY ]    [ RIGGING & ANIMATION ]    [ DYNAMICS & HULLS ]
       • Ax + By + Cz + D = 0    • Skeletal Meshes (.psk)   • Scout Cylinder (42x80)
       • Outward Normals         • Vertex Morph (_d.3d)     • Karma Rigid Bodies
       • Clockwise Winding       • Spline Matinee Tracks    • Ragdoll Transitions
                │                        │                        │
                └────────────────────────┼────────────────────────┘
                                         ▼
                          [ RUNTIME PERFORMANCE OPTIMIZATION ]
                     • Continuous LOD Distance Transitions
                     • Zero-BSP-Cut Semi-Solid Detail (Flags=32)
                     • 75% Engine Budget Law Mathematical Bounding
```

---

## 📐 CSG Geometry & Watertight BSP Mathematics

In Unreal's CSG architecture, every brush is a bounded polyhedral volume enclosed by oriented polygonal planar facets.

### 1. The Mathematical Plane Equation
Every polygon face must satisfy the continuous 3D plane equation:
$$Ax + By + Cz + D = 0$$
where $\vec{n} = (A, B, C)$ is the normalized outward unit normal vector, and $D = -(\vec{n} \cdot \vec{v}_0)$.

### 2. Normal Vector & Vertex Winding Rule
* **Outward Normal Calculation**: Given vertices $\vec{v}_0, \vec{v}_1, \vec{v}_2$:
  $$\vec{n} = (\vec{v}_1 - \vec{v}_0) \times (\vec{v}_2 - \vec{v}_0)$$
* **Clockwise Winding**: Looking at the exterior of the solid brush from the outside, vertices must be ordered **clockwise**. If vertices are wound counter-clockwise, the normal points inward, causing the BSP compiler to invert inside/outside volumes and create catastrophic Hall-of-Mirrors (HOM) defects.

### 3. Non-Planar Quad Triangulation
If four vertices of a quad do not satisfy $Ax_3 + By_3 + Cz_3 + D \approx 0$ within tolerance ($\epsilon = 0.001$), the quad is warped. Warped quads cause non-planar BSP slivers.
* **Remediation**: Split the quad into two planar triangles along the diagonal:
  $$\text{Triangle 1: } (\vec{v}_0, \vec{v}_1, \vec{v}_2) \quad | \quad \text{Triangle 2: } (\vec{v}_0, \vec{v}_2, \vec{v}_3)$$

---

## 🦴 Skeletal Meshes vs. Vertex Animation

Unreal Engine spans two historic paradigms of 3D mesh animation:

### 1. Vertex Animation (Classic UE1 / UT99)
* **Mechanics**: Pre-skeletal deformation where raw 3D vertex positions are recorded frame-by-frame (`_d.3d` data and `_a.3d` animation headers).
* **Interpolation**: UnrealEd dynamically lerps vertex coordinates between keyframes at runtime:
  $$\vec{P}(t) = \vec{V}_{\text{frame } A} + t \cdot (\vec{V}_{\text{frame } B} - \vec{V}_{\text{frame } A})$$
* **Advantages**: Zero matrix transformation overhead; ideal for high-speed tournament combatants and low-spec environments.

### 2. Skeletal Meshes & Bone Hierarchies (UE2.0 through UE5)
* **Mechanics**: Hierarchical skeleton where each bone has local translation and rotation relative to its parent bone. Vertices carry bone indices and skinning weights $\sum w_i = 1.0$.
* **Dual Quaternion / Linear Skinning**: Prevents candy-wrapper collapse at twisting joints (shoulders, wrists).
* **Format**: Exported via ActorX as `.psk` (geometry & skeleton) and `.psa` (animation cycles).

---

## 🥊 Collision Hulls & Spatial Probes

Never attach raw complex visual polygon meshes to dynamic collision queries.

1. **Player Scout Cylinder**: In UE1/UE2.5, navigation reachability and collision queries use standard Scout dimensions:
   $$\text{CollisionRadius} = 42.0 \text{ UU} \quad | \quad \text{CollisionHeight} = 80.0 \text{ UU}$$
2. **Oriented Bounding Boxes (OBB)**: Tight rectangular bounding volumes aligned with local actor rotation for vehicles and moving doors.
3. **Convex Collision Hulls**: For intricate architectural statues and boulders, generate low-poly convex hulls (12–24 faces) to prevent CPU hitching during projectile traces.

---

## 🚗 Karma Physics Dynamics & Ragdoll Simulation (UE2.5 / UT2004)

Unreal Engine 2.5 integrates the MathEngine Karma physics suite:
* **Rigid Bodies (`KarmaActor`)**: Physical simulation with Mass, Center of Mass, Inertia Tensor, Friction, and Restitution.
* **Joint Constraints**:
  * `KHinge`: Revolute joint with angular limits for swinging drawbridges and heavy dungeon doors.
  * `KCarWheelJoint`: Suspension spring and damper for Onslaught ground vehicles (Scorpion, Hellbender).
  * `KBSJoint`: Ball-and-socket joint for multi-link chains and chandeliers.
* **Ragdoll Physics**: Upon lethal damage, pawn controllers call `KMakeRagdoll()`, transferring skeletal bone matrices directly into a physical articulated ragdoll constraint tree.

---

## 🎬 Cinematic Matinee & Sequencer Orchestration

For level intros, flybys, and narrative cutscenes:
* **Camera Paths**: Place `InterpolationPoint` actors sequentially along a 3D spline trajectory.
* **Keyframing**: Define `Position`, `TargetOrientation`, `FOVAngle` (default 90°, zoomed 35°), and `SpeedModifier`.
* **Director Track**: Use `InterpolatingActor` or modern Sequencer cameras to achieve smooth multi-viewport cuts.
