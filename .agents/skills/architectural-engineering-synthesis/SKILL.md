---
name: architectural-engineering-synthesis
description: World-class architectural engineering, structural loads, spatial topology, defensive fortification grammar, classical orders, and gothic structural synthesis for Unreal level design.
---

# Architectural Engineering Synthesis Skill

## Overview

The **Architectural Engineering Synthesis Skill** equips Unreal level designers and autonomous agents with rigorous civil, military, and classical architectural engineering principles. It translates architectural theory into watertight Constructive Solid Geometry (CSG), preventing floating structures, spatial disorientation, unrealistic weight distributions, and engine-crashing geometry.

```
                           [ ARCHITECTURAL ORDERS & STYLES ]
                  ┌────────────────────────┼────────────────────────┐
                  ▼                        ▼                        ▼
        [ CLASSICAL ANTIQUITY ]   [ GOTHIC STRUCTURAL ]    [ MEDIEVAL DEFENSIVE ]
        • Doric (1:8 ratio)       • Pointed Arches         • Curtain Walls (128 UU)
        • Ionic (Volutes)         • Ribbed Groin Vaults    • Octagonal Bastions
        • Corinthian (Acanthus)   • Flying Buttresses      • Barbican Chokepoints
                  │                        │                        │
                  └────────────────────────┼────────────────────────┘
                                           ▼
                            [ STRUCTURAL LOAD & TOPOLOGY ]
                       • Vertical Gravity & Bedrock Grounding
                       • Lateral Thrust Dissipation
                       • Chokepoint Triad (Approach → Threshold → Exit)
                       • Sightline Bounding & Combat Dais Elevation
```

---

## 🏛️ Foundational Engineering Directives

### 1. The Bedrock Grounding Law (Anti-Void Anchor)
* **Rule**: Architecture must never float or terminate in mid-air over voids.
* **Implementation**: Every stone structure, castle wall, or temple colonnade must be anchored into solid bedrock bluffs, stepped stone plinths, or terraformed terrain ramps.
* **CSG Pattern**:
  ```text
  // Anchor fortress bluff to valley bedrock
  BRUSH MOVETO X=1024 Y=0 Z=-384
  BRUSH ADDCUBE X=1280 Y=1024 Z=512
  ```

### 2. Classical Orders & Column Proportions
When synthesizing temples, civic rotundas, or grand sanctuaries:
* **Doric Order**: Sturdy, fluted shaft, plain circular echinus capital. Height-to-diameter ratio: `1:8` (e.g., Radius 32 UU, Height 256 UU). Use for defensive bastions, fortress gates, and subterranean crypts.
* **Ionic Order**: Slender fluting, scroll-like volute capitals, dentil cornice friezes. Ratio: `1:9` (e.g., Radius 28 UU, Height 252 UU). Use for libraries, archives, and mid-tier temple courtyards.
* **Corinthian Order**: Elaborate double-tier acanthus leaf capitals, enriched entablatures. Ratio: `1:10` (e.g., Radius 24 UU, Height 240 UU). Use for central altars, high shrines, and sovereign throne chambers.

---

## 🏰 Gothic Structural Grammar (Concentrated Thrust Systems)

Gothic architecture was a revolution in structural engineering that replaced massive solid walls with concentrated skeletal frameworks:

### 1. Pointed Arch Mechanics
* **Physics**: Unlike round Roman arches that direct immense lateral outward thrust requiring massive walls, pointed arches reduce lateral outward thrust by 50% and channel forces vertically downward.
* **CSG Profile**: Intersecting twin circular arcs with center points offset by half the span.
* **Ratio**: Height-to-width `2:1` (Span 256 UU, Apex Height 512 UU).

### 2. Ribbed Groin Vaulting
* **Engineering**: Diagonal ogive stone ribs concentrate roof weight onto four corner piers rather than continuous walls.
* **CSG Construction**: Subtractive vaulted bay ceiling crossed with semi-solid decorative arch ribs (`PF_Semisolid = 32`).

### 3. Flying Buttress & Pier Pinnacles
* **Engineering**: Exterior flyers span open airspace above side aisles, carrying vault thrust to exterior masonry piers. Heavy stone pinnacles atop piers supply downward vertical compression to keep the resultant thrust vector safely within the pier's center-of-gravity kern.
* **Execution**: Model flyer arms as semi-solid beveled trusses.

---

## 🛡️ Medieval Military Fortifications & Castle Topology

Authentic castle engineering employs **Defense-in-Depth** and **Enfilade Crossfire**:

```
[ OUTER MOAT / RAVINE ]  ──►  [ BARBICAN & DRAWBRIDGE ]  ──►  [ PORTCULLIS GATEHOUSE ]
                                                                      │
[ INNER SANCTUARY KEEP ]  ◄──  [ ENCLOSED INNER BAILEY ]  ◄───────────┘
```

1. **Curtain Walls**: Minimum 128 UU thickness, height 384–512 UU. Topped with an allure walkway (width 64 UU).
2. **Crenellated Battlements & Merlons**: Solid merlon blocks (Height 64 UU, Width 48 UU) spaced with embrasure gaps (Width 32 UU) providing 85% cover for archers.
3. **Flanking Bastions (Octagonal Towers)**: Extend outward from curtain wall corners by 128–256 UU to eliminate blind spots along wall bases.
4. **Gatehouse & Barbican**: Double-gate defense with portcullis slot, murder holes in the ceiling for vertical counter-measures, and splayed arrow slits (`PF_TwoSided` sheet brushes).
5. **Machicolations**: Projecting stone parapets supported by corbels with open floor slots overlooking wall footings.

---

## 🏭 Sci-Fi & Industrial Brutalism

For high-tech bases, reactor complexes, and starships:
* **Cantilever Overhangs**: Deep triangular structural gussets supporting overhung landing decks without ground columns.
* **Hexagonal Blast Bulkheads**: 6-sided beveled door frames resisting explosive overpressure.
* **Conduit & Pipe Racks**: Overhead suspended gantry catwalks (`PF_Semisolid`) running high-voltage wiring, coolant lines, and ventilation ducts.

---

## 📐 Spatial Topology, Sightlines & Chokepoint Triads

Every competitive or narrative level must govern player flow through the **Chokepoint Triad**:
1. **Approach Zone (Cover & Staging)**: Multi-angle approach lanes with low cover crates/boulders (height 48–64 UU).
2. **Threshold Bottleneck**: Tight passage (width 128–192 UU) concentrating fire and demanding tactical commitment.
3. **Exit Distribution (Tactical Vantage)**: Opening into wider chambers with branching egress, sniper overlooks, and high ground.

### Combat Dais Elevation Rule
Central combat areas or weapon spawns must be placed on a raised dais elevated **+32 to +64 UU** above surrounding floors. This creates immediate visual hierarchy and tactical dominance while allowing players to smoothly step up without jumping.
