# Push Geometry to 75% of Editor Limits — Intelligent Self-Inquiry Design

## The Hard Questions First

Before writing a single line of code, I asked myself the questions that separate great maps from forgettable ones:

> **Q: What actually makes DM-Deck16][ feel like a masterpiece?**
> A: Not polygon count. Elliot "Myscha" Cannon built it in *half a day*. It's the **flow** — tight-to-open transitions, vertical connectivity, natural choke points around power-ups, and distinct visual landmarks in every room so you never feel lost.

> **Q: Why do community masterworks like DOM-Tenshutaishite and DM-Abraxas take your breath away?**
> A: Because they use BSP as an *artistic medium*, not just a construction tool. Arches instead of flat openings. Trim strips where walls meet floors. Recessed lighting alcoves that cast dramatic shadows. Stepped cliff faces instead of flat walls. Every surface has *intent*.

> **Q: What's the difference between "more polygons" and "more detail"?**
> A: More polygons can make things *worse* — more BSP cuts, more HOM glitches, more rebuild time. True detail comes from **architectural intent**: trim pieces, molding, beveled edges, alcoves, semi-solid decoration, and varied floor heights. The legendary mappers used *fewer* solid brushes but *more* semi-solid decorative brushes.

> **Q: What's the actual ceiling before the editor fights back?**
> A: 65,536 BSP nodes hard limit. Performance degrades past ~50K polygons. Semi-solids don't cut BSP, so they're essentially *free detail*. Zone portals let you build massive maps by culling invisible zones. The real strategy is: **structural solid brushes for rooms + semi-solid brushes for decoration + zone portals for scale**.

---

## The Architecture of Beauty

### What Epic's and the Community's Best Mappers Actually Do

| Technique | What It Is | Why It Matters | Our Generators Today |
|:---|:---|:---|:---|
| **Trim / Molding Strips** | Thin ADD brushes along wall-floor and wall-ceiling joints | Breaks up flat surfaces, adds architectural realism | ❌ Missing entirely |
| **Semi-Solid Decoration** | Pillars, columns, buttresses that don't cut BSP | Massive visual detail at zero BSP cost | ❌ All brushes are solid |
| **Recessed Lighting Alcoves** | Small SUBTRACT niches in walls with lights inside | Creates dramatic shadows and environmental storytelling | ❌ Lights float in open air |
| **Arched Doorways** | Half-cylinder subtracted from wall tops | Transforms boxy corridors into architecture | ❌ All openings are rectangular |
| **Stepped Cliff Terracing** | Multiple graduated ledge brushes per cliff face | Mountains look like mountains, not flat walls | ❌ Single box per cliff |
| **Zone Portals** | Sheet brushes in doorways dividing visibility zones | Allows 3× larger maps without performance hit | ❌ Not implemented |
| **Varied Floor Heights** | Subtle 32–64 UU elevation changes within rooms | Creates natural cover and visual interest | ❌ All floors are flat |
| **Multi-Zone Ambient Lighting** | Different light colour/intensity per architectural zone | Each area has distinct atmosphere | ⚠️ Basic (4–6 lights) |
| **Dense PathNode Lattice** | 40–64 PathNodes with strategic InventorySpot/Ambush | Bots play like humans, know flanking routes | ⚠️ Sparse (15–32 nodes) |

---

## Proposed Changes

### 1. Semi-Solid Brush Support — The Game Changer

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py) — Core T3D Generator

The single most impactful change. Semi-solid brushes add geometry without cutting BSP — meaning we can add **dozens** of decorative elements (pillars, trim, molding, buttresses) at essentially zero BSP compilation cost.

**New command**: `BRUSH ADDSEMISOLID` (or `BRUSH ADD` with `PolyFlags=32`)

```python
# New helper: writes a semi-solid decorative brush
def _write_semisolid_brush_file(system_dir, filename, dimensions, **kwargs):
    """Generates a semi-solid brush T3D — adds geometry without cutting BSP."""
    # Same PolyList generation, but with PolyFlags=32 on all faces
    ...
```

**Impact on BSP node count**: Zero. Semi-solids are processed *after* the BSP tree is built.

---

### 2. New Architectural Primitives

#### [MODIFY] [formula_engine.py](file:///d:/Projects/unrealagentharness/core/formula_engine.py) — `_generate_brush_polylist_t3d()`

| New Shape | Faces | Technique | Use Case |
|:---|---:|:---|:---|
| `Arch` | 10–16 | Half-cylinder top + rectangular bottom | Doorways, bridge underpasses, window frames |
| `TrimStrip` | 6 | Thin box (e.g. 16×width×height) | Wall-floor molding, ceiling cornices |
| `SteppedCliff` | 12–18 | 3–4 stacked boxes with decreasing width | Mountain cliff faces, terraced terrain |
| `BeveledBox` | 18 | Cube with 45° chamfered edges | Premium pillars, platform edges |
| `Buttress` | 8 | Tapered wedge | Castle wall supports, flying buttresses |
| `Niche` | 10 | Small recessed alcove | Lighting recesses, weapon display alcoves |

---

### 3. Detail Level Configuration System

```python
DETAIL_PRESETS = {
    "standard": {   # Backward compatible — current output
        "cylinder_sides": 16,
        "pillar_sides": 12,
        "tower_sides": 8,
        "trim_enabled": False,
        "semisolid_decoration": False,
        "alcove_lighting": False,
        "arched_doorways": False,
        "stepped_cliffs": False,
        "zone_portals": False,
        "extra_pathnodes": False,
        "light_density": "sparse",    # 4-6 lights
    },
    "high": {       # DEFAULT — dramatically richer architecture
        "cylinder_sides": 32,
        "pillar_sides": 24,
        "tower_sides": 16,
        "trim_enabled": True,         # Wall-floor and wall-ceiling trim strips
        "semisolid_decoration": True, # Decorative pillars, buttresses, columns
        "alcove_lighting": True,      # Recessed wall niches with inset lights
        "arched_doorways": True,      # Half-cylinder arched corridor ceilings
        "stepped_cliffs": True,       # Multi-tier cliff terracing
        "zone_portals": False,        # Not yet (Phase 3)
        "extra_pathnodes": True,      # 40-64 PathNodes per map
        "light_density": "rich",      # 16-24 lights with accent/rim fills
    },
    "ultra": {      # 75% of editor limits — maximum artistry
        "cylinder_sides": 48,
        "pillar_sides": 32,
        "tower_sides": 24,
        "trim_enabled": True,
        "semisolid_decoration": True,
        "alcove_lighting": True,
        "arched_doorways": True,
        "stepped_cliffs": True,
        "zone_portals": True,         # Full zone portal visibility culling
        "extra_pathnodes": True,      # 50-64 PathNodes per map
        "light_density": "cinematic", # 24-32 lights with dramatic shadow-casting
    },
}
```

Every generator gets `detail_level="high"` as the new default.

---

### 4. Indoor Arena Enhancement (generate_ut99_tournament_arena)

**Current**: 6 solid brushes, 6 PlayerStarts, 4 lights, 19 PathNodes
**Target (high)**: ~30 brushes (8 solid + 22 semi-solid), 8 PS, 20 lights, 42 PathNodes

New architectural elements:
- **4 wall-floor trim strips** (semi-solid) — thin beveled strips along base of all walls
- **4 wall-ceiling cornice strips** (semi-solid) — decorative crown molding
- **4 corner pillar columns** (semi-solid, 24-sided cylinders) — structural landmarks
- **2 arched doorway entries** — half-cylinder subtracted from corridor ceiling
- **8 recessed wall lighting alcoves** — small subtracted niches with inset light actors
- **4 beveled platform edges** on the mezzanine and dais
- **Elevated sniper gallery** with staircase access and railing trim
- **Central elevated octagonal dais** with higher tessellation (16–24 sides)
- **Doubled PathNode density** with strategic InventorySpot placement
- **3-layer lighting**: Key (directional), Fill (ambient), Accent (colored rim)

---

### 5. Outdoor Terrain Enhancement (generate_ut99_verdant_mountain_valley)

**Current**: 25 solid brushes, 6 PS, 6 lights, 29 PathNodes, 22 decorative actors
**Target (high)**: ~65 brushes (28 solid + 37 semi-solid), 8 PS, 24 lights, 52 PathNodes, 44 decorative actors

New terrain/architectural elements:
- **Stepped cliff terracing** — each cliff face becomes 3–4 graduated ledge brushes
- **Mountain cave alcoves** — 2–3 small subtracted grottos carved into cliff walls
- **Decorative bridge arch underside** (semi-solid) — arch rib under the stone bridge
- **Castle inner courtyard** — secondary subtracted interior with fountain dais
- **Crenellation / merlon wall walk** — thin semi-solid brushes forming battlements
- **River stepping stones** — small semi-solid box brushes in the gorge
- **Castle window frames** — thin semi-solid trim around tower windows
- **Flying buttresses** — tapered semi-solid wedges on castle exterior walls
- **3× foliage density** — 36+ trees, 16+ plants, 16+ boulders with varied placement
- **Per-tower rim lighting** — warm accent lights crowning each tower
- **Torch-cast wall wash** — additional lights near torch actors for realism

---

### 6. Configuration Integration

#### [MODIFY] [config/llm_profiles.json](file:///d:/Projects/unrealagentharness/config/llm_profiles.json)
- Add `"default_detail_level": "high"` to each LLM profile

#### [MODIFY] [core/tools_schema.py](file:///d:/Projects/unrealagentharness/core/tools_schema.py)
- Add `detail_level` parameter (`"standard"`, `"high"`, `"ultra"`) to generation tools
- The LLM can explicitly request maximum artistry

---

### 7. Test & Documentation Updates

#### [MODIFY] [test_harness.py](file:///d:/Projects/unrealagentharness/test_harness.py)
- Test detail level presets exist and are well-formed
- Verify `high` detail arena produces >2× the brushes/actors vs `standard`
- Test new brush primitives (Arch, TrimStrip, BeveledBox, SteppedCliff, Niche)
- Test semi-solid flag (PolyFlags=32) appears in semi-solid brush output

#### [MODIFY] [CHANGELOG.md](file:///d:/Projects/unrealagentharness/CHANGELOG.md) & [docs/CHANGELOG.md](file:///d:/Projects/unrealagentharness/docs/CHANGELOG.md)
#### [MODIFY] [version.py](file:///d:/Projects/unrealagentharness/version.py) → `2.16.0`

---

## Open Questions

> [!IMPORTANT]
> **Default detail**: Should the new default be `"high"` (recommended — dramatically richer while safe) or `"ultra"` (75% of limits — maximum artistry, longest rebuild times)?

> [!NOTE]
> **UT2004 generators**: UE2.5 has ~3× higher BSP limits than UE1. Should UT2004 generators default to `"ultra"` while UE1 defaults to `"high"`?

> [!NOTE]
> **Semi-solid pillars**: Should the existing solid pillar brushes be converted to semi-solid (reducing BSP cuts) or kept as solid for collision fidelity?

## Verification Plan

### Automated Tests
```bash
python test_harness.py -v
```
- All 75 existing tests pass (backward compat)
- New detail-level and semi-solid tests pass

### Manual Verification
- Generate a `high` detail arena and verify BSP rebuild succeeds without HOM
- Compare brush/actor count between `standard` and `high` output
