r"""
UAH Learning Engine & "Unreal Academy of Master Design".
Autonomous knowledge ingestion, research, study, and training system for the Agent Harness.
Ingests, categorizes, indexes, and queries:
  1. 📚 Tutorials & Fundamentals (UE1-UE5 CSG, BSP geometry, UnrealScript, Bot Navigation).
  2. 💡 Tips, Tricks & Best Practices (Brush alignment, lightmap optimizations, Sheet glass, Zone portals).
  3. 🕵️ Little-Known Facts & Engine Quirks (Fake Backdrop clipping, BSP cut order, GPF crash mitigations).
  4. 🎭 Artistic Detail, 3D Illusions & FX Tricks (Forced perspective skyboxes, infinite mirror halls, volumetric light shafts, parallax voids).
  5. 🏆 Classic Map Deconstructions (DM-Deck16][, CTF-Face, DM-Morpheus, Chizra Temple, ONS-Torlan, Bluff Eversmoking).
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import get_logger
from .memory_engine import MemoryEngine

logger = get_logger("LearningEngine", "learning_engine.log")


class LearningEngine:
    """Master research, training, and knowledge ingestion engine for the Unreal Agent Harness."""

    CATEGORIES = [
        "tutorials",
        "tips_and_tricks",
        "little_known_facts",
        "artistic_illusions_fx",
        "classic_map_deconstructions",
        "engine_secrets",
    ]

    def __init__(self, memory_engine: Optional[MemoryEngine] = None):
        self.memory_engine = memory_engine or MemoryEngine()
        self._ensure_curriculum_seeded()

    def ingest_knowledge_entry(
        self,
        category: str,
        title: str,
        summary: str,
        engine_target: str = "All (UE1-UE5)",
        step_by_step: Optional[List[str]] = None,
        technical_trick: Optional[str] = None,
        t3d_commands: Optional[List[str]] = None,
        tags: str = "",
        author_reference: str = "Community Wisdom",
    ) -> bool:
        """Ingests and formalizes a new master technique, trick, or study record into the lifelong SQLite knowledgebase."""
        if category not in self.CATEGORIES:
            category = "tips_and_tricks"

        payload = {
            "title": title,
            "category": category,
            "summary": summary,
            "engine_target": engine_target,
            "step_by_step": step_by_step or [],
            "technical_trick": technical_trick or "",
            "t3d_commands": t3d_commands or [],
            "tags": tags,
            "author_reference": author_reference,
            "ingested_at": time.time(),
        }

        content_json = json.dumps(payload, indent=2)
        success = self.memory_engine.record_wisdom(
            category=f"academy_{category}",
            title=title,
            content=content_json,
            tags=f"academy,{category},{tags}",
            confidence=1.0,
        )

        if success:
            logger.info(f"LearningEngine ingested: '{title}' [{category}] ({engine_target})")
        else:
            logger.error(f"LearningEngine failed to ingest: '{title}'")

        return success

    def query_academy(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 15,
    ) -> List[Dict[str, Any]]:
        """Queries the master academy curriculum and ingested research items."""
        cat_filter = f"academy_{category}" if category else "academy_"
        results = self.memory_engine.query_wisdom(query=query, category=cat_filter, limit=limit)

        entries = []
        for r in results:
            try:
                data = json.loads(r["content"])
                data["id"] = r["id"]
                data["confidence"] = r["confidence"]
                entries.append(data)
            except Exception:
                pass
        return entries

    def get_all_entries_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retrieves all curriculum entries for a specific category."""
        return self.query_academy("", category=category, limit=100)

    def _ensure_curriculum_seeded(self):
        """Pre-seeds the lifelong memory with legendary Unreal techniques, 3D illusions, and classic map recipes."""
        existing = self.memory_engine.query_wisdom("academy_", limit=1)
        if existing:
            return  # Already seeded

        logger.info("Seeding Master Unreal Academy Curriculum & Hall of Fame Tricks...")

        # ---------------------------------------------------------------------
        # 1. 🎭 ARTISTIC DETAIL & 3D ILLUSION FX TRICKS
        # ---------------------------------------------------------------------
        self.ingest_knowledge_entry(
            category="artistic_illusions_fx",
            title="🪐 Forced-Perspective Planetary Skybox Illusion",
            summary="Creates a monumental 3D planetary body looming over the player arena using a 1:16 scaled skybox housing a high-radius hemisphere and rotating cloud sheet.",
            engine_target="UE1 / UE2.5 / UE5",
            step_by_step=[
                "1. Subtract a 1024x1024x1024 cube far outside the arena bounds to serve as SkyZone housing.",
                "2. Place an `Engine.SkyZoneInfo` actor at the exact center (0, 0, 0) of the skybox room.",
                "3. Add a semi-solid cylinder or hemisphere (radius=384, height=128) painted with planetary terrain texture.",
                "4. Add a rotating 2D planar sheet above it with translucent cloud alpha texture (`bUnlit=True`, `Style=STY_Translucent`).",
                "5. In the main player map, paint the sky ceiling surface and flag it with `bFakeBackdrop=True` in Surface Properties.",
                "6. The engine projects the skybox room into infinity with parallax motion as the player runs across the map.",
            ],
            technical_trick="Set SkyZoneInfo `bClipStaticMeshes=True` in UT2004 to prevent skybox objects from leaking into world depth buffers.",
            t3d_commands=[
                "BRUSH MOVETO X=16384 Y=16384 Z=16384",
                "BRUSH SUBTRACT",
                "ACTOR ADD CLASS=Engine.SkyZoneInfo",
            ],
            tags="skybox,forced_perspective,illusion,3d_planet,space",
            author_reference="Shane Caudle & Cliff Bleszinski (CTF-Face)",
        )

        self.ingest_knowledge_entry(
            category="artistic_illusions_fx",
            title="🪞 Infinite Mirror Portal Corridor (WarpZone Illusion)",
            summary="Creates an Escher-like infinite hallway or seamless teleporter doorway using paired WarpZoneInfo actors with matching otherSideURL tags.",
            engine_target="UE1 (UT99 / Unreal 1)",
            step_by_step=[
                "1. Carve two separate rooms or hallway ends with identical cross-section dimensions.",
                "2. At each entrance plane, add a special 2D sheet brush tagged as a Zone Portal.",
                "3. In each isolated zone, place an `Engine.WarpZoneInfo` actor.",
                "4. Set `WarpZoneInfo1.ThisZone = 'PortalA'` and `WarpZoneInfo1.OtherSideURL = 'PortalB'`.",
                "5. Set `WarpZoneInfo2.ThisZone = 'PortalB'` and `WarpZoneInfo2.OtherSideURL = 'PortalA'`.",
                "6. The camera seamlessly renders the remote room through the portal with 100% ray and player momentum conservation.",
            ],
            technical_trick="Align the surface texture of both zone portals to 0,0 offset so players experience zero visual seam or stutter when walking through.",
            tags="warpzone,portal,mirror,infinite_hallway,dimension_door",
            author_reference="Epic Games (DM-Morpheus / Unreal 1 Tech)",
        )

        self.ingest_knowledge_entry(
            category="artistic_illusions_fx",
            title="💡 Volumetric Light Shafts (Sunbeams & Neon Glow)",
            summary="Creates the 3D optical illusion of volumetric atmospheric god-rays and glowing dust motes using layered semi-solid sheets with gradient alpha textures.",
            engine_target="UE1 / UE2.5",
            step_by_step=[
                "1. Build a skylight, Gothic rose window, or broken roof portal.",
                "2. Create a planar Sheet brush oriented at a 45-degree angle descending from the window to the floor.",
                "3. Apply a directional gradient alpha texture (e.g. `ShaneFX.Beam1` or `UTtech1.Glow`).",
                "4. In Surface Properties, enable `Translucent=True`, `Unlit=True`, and `TwoSided=True`.",
                "5. Place an `Engine.Light` at the window origin with high brightness and complementary hue.",
            ],
            technical_trick="Never use solid subtractive/additive brushes for light rays; semi-solid or non-solid sheets produce zero BSP cuts and zero polygon tearing.",
            tags="lighting,god_rays,volumetric,sunbeams,atmosphere",
            author_reference="Hourences & Epic Games (Temple of Vandora)",
        )

        # ---------------------------------------------------------------------
        # 2. 🏆 CLASSIC MAP DECONSTRUCTIONS (U1 - U5)
        # ---------------------------------------------------------------------
        self.ingest_knowledge_entry(
            category="classic_map_deconstructions",
            title="🏰 CTF-Face (Facing Worlds) Deconstruction",
            summary="The most famous capture-the-flag level in FPS history: Two towering monolithic sniper spires in orbital asteroid space connected by high-exposure floating bridges.",
            engine_target="UT99 / UT2004 / UE5",
            step_by_step=[
                "1. Dual-Asteroid Spatial Separation: 8192 UU gap between Red and Blue monolith towers.",
                "2. Verticality Triad: Basement flag room $\rightarrow$ Ground level entrance teleporters $\rightarrow$ Upper sniper perch (3 tiers).",
                "3. High-Ground Vulnerability: The sniper balcony offers unobstructed sightlines across the entire level, but leaves snipers 100% exposed to counter-sniping.",
                "4. Midfield Chokepoint: The narrow floating stone bridge forces players into high-risk rocket and sniper duels.",
            ],
            technical_trick="Place `SpecialEvent` play-sound triggers on the bridge arches and use low-mass gravity modifiers in the asteroid base zones.",
            tags="facing_worlds,ctf_face,sniper_perch,monolith,classic_map",
            author_reference="Cedric 'Inoxx' Fiorentino (1999)",
        )

        self.ingest_knowledge_entry(
            category="classic_map_deconstructions",
            title="🧪 DM-Deck16][ (Deck 16) Deconstruction",
            summary="The definitive Deathmatch level: Multi-tier industrial slime factory with central acid pool, teleporter loops, and the legendary high-risk UDamage / Flak Cannon perch.",
            engine_target="Unreal 1 / UT99 / UT2004 / UT4",
            step_by_step=[
                "1. Centerpiece Acid Hazard: Central Green Slime vat (`WaterZone` with `PainType=GreenSlime`, `DamagePerSec=20`).",
                "2. Asymmetrical Multi-Tier Looping: Three distinct elevation tiers connected by ramps, lifts, and jump pads.",
                "3. The King of the Hill Perch: The upper UDamage ledge requires a precarious lift ride and gives commanding control over the main vat.",
                "4. Secret Teleporter Escape: Submerged pipe teleporter at the bottom of the acid vat provides a high-risk getaway.",
            ],
            technical_trick="Use `ZoneVelocity` in the acid canal to gently push falling players into the slime filtration grinder.",
            tags="deck16,deathmatch,slime_vat,udamage,asymmetry,classic_map",
            author_reference="Elliot 'Myscha the Sleddog' Cannon (1998)",
        )

        # ---------------------------------------------------------------------
        # 3. 💡 TIPS, TRICKS & SUGGESTIONS
        # ---------------------------------------------------------------------
        self.ingest_knowledge_entry(
            category="tips_and_tricks",
            title="🛡️ The 75% Engine Limit Golden Rule",
            summary="The mathematical ceiling for stable procedural CSG geometry: Never exceed 75% of maximum node counts or actor allocations to ensure 100% crash-free compilation.",
            engine_target="UE1 / UE2.5",
            step_by_step=[
                "1. In UE1 (UT99), the hard engine node limit is 65,536 nodes; target maximum is 49,152 nodes.",
                "2. In UE2.5 (UT2004), the visible node limit is 131,072 nodes; target maximum is 98,304 nodes.",
                "3. In complex rooms, convert architectural decorative pillars, moldings, and trim to `Semi-Solid` brushes (`BRUSH ADD FLAGS=32`).",
                "4. Semi-solid brushes do NOT cut into surrounding world polygons, eliminating 80% of BSP node bloat.",
            ],
            technical_trick="Run `MAP CHECK` after every major architectural wing addition to verify zero coplanar poly overlaps.",
            tags="optimization,bsp_cuts,semi_solid,75_percent_rule,stability",
            author_reference="UAH Core Engineering Standard",
        )

        self.ingest_knowledge_entry(
            category="tips_and_tricks",
            title="⚡ Preventing Bot Navigational Dead-Ends (The 650 UU Law)",
            summary="Ensures 100% bot reachability across complex multi-floor levels by maintaining line-of-sight spacing under 650 Unreal Units between PathNodes.",
            engine_target="UE1 / UE2.0 / UE2.5",
            step_by_step=[
                "1. Place PathNodes at a maximum distance of 650 UU (engine max is 1000 UU, but 650 UU guarantees flawless ReachSpecs).",
                "2. Always elevate PathNodes +30 UU above the floor plane to prevent actors from embedding into brush collision planes.",
                "3. For doorways, place a PathNode directly in the door threshold and one node 128 UU on either side.",
                "4. Run `PATHS BUILD` (UE1) or `PATHS DEFINE` (UT2004) followed by `FLUSH`.",
            ],
            technical_trick="Never place raw `PlayerStart` actors directly touching the floor; always give +50 UU clearance to avoid spawned bots getting stuck in geometry.",
            tags="pathing,botpack,reachspecs,navigation,ai_flow",
            author_reference="Steve Polge & Erik de Neve (Unreal Bot AI)",
        )

        # ---------------------------------------------------------------------
        # 4. 🕵️ LITTLE-KNOWN FACTS & ENGINE QUIRKS
        # ---------------------------------------------------------------------
        self.ingest_knowledge_entry(
            category="little_known_facts",
            title="🐛 The UT2004 LevelInfo AIController Crash Mystery",
            summary="Why running PATHS BUILD in UnrealEd 3.0 crashes with 'Actor not found: AIController MyLevel.AIController1' if LevelInfo is missing.",
            engine_target="UT2004 / UT2003 (UE2.5)",
            step_by_step=[
                "1. During path compilation, `FPathBuilder::buildPaths` spawns a temporary `AIController` to calculate jump clearances.",
                "2. When destroying the controller, `ULevel::DestroyActor` attempts to locate the root singleton `Engine.LevelInfo`.",
                "3. If `LevelInfo` is missing, the controller index lookup fails with a General Protection Fault (0xC0000005).",
                "4. Solution: Always ensure `Begin Actor Class=LevelInfo` is the very first entry in the actor import map.",
            ],
            technical_trick="Use `PATHS DEFINE` instead of raw `PATHS BUILD` in UT2004 scripts to invoke the non-destructive path compiler.",
            tags="crash_fix,ut2004,levelinfo,aicontroller,paths_define,little_known_fact",
            author_reference="UAH Diagnostics & Kirk LaSalle (2026)",
        )

        # ---------------------------------------------------------------------
        # 5. ⚙️ UNREAL PROCEDURAL TECHNOLOGY (UE1/UT99 CONDENSED SYNTHESIS)
        # ---------------------------------------------------------------------
        self.ingest_knowledge_entry(

            category="tutorials",
            title="🌌 Hierarchical Procedural CSG Stack (Macro-to-Micro Decomposition)",
            summary="Condenses modern PCG graph generation down to the UE1 5-layer subtractive/additive CSG pipeline for guaranteed crash-free procedural level generation.",
            engine_target="UE1 / UT99 / OldUnreal 469e",
            step_by_step=[
                "1. Master Subtractive Hull: Carve the primary negative bounding void (e.g. Canyon 4608x4608x1792) out of solid universe bedrock.",
                "2. Structural Additive Anchors: Add solid bedrock promontories, mountain shelves, and fortress foundations using granite bedrock textures.",
                "3. Functional Negative Carves: Subtract interior halls, chasm ravines, stairwells, and gatehouse corridors into the bedrock.",
                "4. Semi-Solid Detail Multipliers: Add columns, battlements, stone arch ribs, and ledges with `Flags=32` (PF_Semisolid) for zero BSP cuts.",
                "5. Non-Solid/Translucent Projections: Add flowing water sheets, river planes, and volumetric rays with `Flags=4` (PF_Translucent) and `Flags=4194432` (PF_FakeBackdrop).",
            ],
            technical_trick="Never place additive structural brushes after semi-solid detail brushes; strict hierarchical ordering prevents BSP node fragmentation.",
            t3d_commands=[
                "BRUSH MOVETO X=0 Y=0 Z=0",
                "BRUSH IMPORT FILE=MasterHull.t3d MERGE=0 FLAGS=0",
                "BRUSH SUBTRACT",
                "BRUSH IMPORT FILE=BedrockBluff.t3d MERGE=0 FLAGS=0",
                "BRUSH ADD",
                "BRUSH IMPORT FILE=CastleHall.t3d MERGE=0 FLAGS=0",
                "BRUSH SUBTRACT",
                "BRUSH IMPORT FILE=BridgeArch.t3d MERGE=0 FLAGS=32",
                "BRUSH ADD",
            ],
            tags="procedural,pcg,csg_hierarchy,macro_to_micro,ue1_architecture",
            author_reference="UAH Procedural Architecture & Kirk LaSalle (2026)",
        )

        self.ingest_knowledge_entry(
            category="tutorials",
            title="🏔️ Procedural Heightfield & Stepped Outdoor Terrain in BSP",
            summary="Synthesizes organic, natural mountain valleys and river chasms in UE1 CSG using stepped beveled terraces and interlocking slope ramps.",
            engine_target="UE1 / UT99 / UE2",
            step_by_step=[
                "1. Base Valley Floor: Carve main canyon basin with grassy rock floor (`GenEarth.grasrok2`) and vertical cliff rock walls (`GenEarth.Rockfac1`).",
                "2. Stepped Terraces: Place multi-tier beveled box volumes along mountain walls to create natural climbable rock shelves.",
                "3. Interlocking Slope Ramps: Bridge elevation tiers with 45-degree and 30-degree ramp primitives to provide smooth bot and player navigation.",
                "4. Central River Chasm: Subtract a 256-384 UU deep channel through the valley floor and cap with translucent water (`GenFluid.Water1`).",
                "5. Rock Boulders: Populate with `UnrealI.BigRock` and `UnrealShare.Boulder` actors at slope inflection points.",
            ],
            technical_trick="Ensure all terrain brush polygon normals are strictly coplanar; warped non-planar quads cause Hall of Mirrors (HOM) errors.",
            tags="procedural_terrain,heightfield,bsp_valleys,stepped_terraces,mountain_cliffs",
            author_reference="Tim Sweeney & UAH Core Architecture",
        )

        self.ingest_knowledge_entry(
            category="artistic_illusions_fx",
            title="🎨 Procedural Atmospheric Radiosity & Complementary Lighting Balance",
            summary="Implements dual-spectrum color harmony and atmospheric radiosity in UnrealEd without expensive raytracing.",
            engine_target="UE1 / UT99 / UE2.5",
            step_by_step=[
                "1. Key Light Spectrum: Place high-elevation sun/torch lights with warm amber hues (`LightHue=20-38`, `LightSaturation=100-220`, `LightBrightness=220-255`).",
                "2. Ambient Sky/Water Bounce Fill: Distribute wide-radius low-intensity cool cyan/blue lights (`LightHue=145-160`, `LightSaturation=140-190`, `LightBrightness=120-180`).",
                "3. Dynamic Fluid Shimmer: Place dedicated `Engine.Light` actors with `LightEffect=LE_WateryShimmer` beneath waterfalls and along riverbeds.",
                "4. Torch Sconces: Attach `LightEffect=LE_TorchWaver` to `UnrealShare.TorchFlame` actors along castle parapets and stone bridge piers.",
                "5. SkyZone Radiant Ambient: Set `ZoneInfo.AmbientBrightness=55` to eliminate pitch-black shadows across outdoor geometry.",
            ],
            technical_trick="Keep `LightRadius` under 160 UU on indoor fixtures to prevent overlapping spherical attenuation leaks across multiple room walls.",
            tags="procedural_lighting,radiosity,color_theory,complementary_hues,shimmer_fx",
            author_reference="Epic Games & UAH Lighting Standards",
        )

        self.ingest_knowledge_entry(
            category="tips_and_tricks",
            title="📐 Watertight BSP Mathematical Laws & Outward Clockwise Winding",
            summary="The mathematical formulation required for 100% crash-free, non-leaking procedural T3D brush generation in Unreal Engine 1.",
            engine_target="UE1 (1998-1999) / OldUnreal 469e",
            step_by_step=[
                "1. Clockwise Outward Winding: All vertex lists must be specified in clockwise order when looking at the polygon face from the outside.",
                "2. Exact Normal Vector: The normal (A, B, C) must equal the normalized cross product: $\\vec{N} = \\frac{(\\vec{V_1} - \\vec{V_0}) \\times (\\vec{V_2} - \\vec{V_0})}{\\|(\\vec{V_1} - \\vec{V_0}) \\times (\\vec{V_2} - \\vec{V_0})\\|}$.",
                "3. Strict Coplanarity: Every vertex $V_i$ on a polygon face must satisfy the plane equation $(\\vec{V_i} - \\vec{V_0}) \\cdot \\vec{N} = 0$.",
                "4. Quad/Tri Triangulation: If 4 vertices are slightly warped, split the polygon into two 3-vertex coplanar triangles.",
                "5. Texture Align Vectors: Define orthogonal `TextureU` and `TextureV` vectors normalized to scale 1.0.",
            ],
            technical_trick="A single inverted normal or counter-clockwise polygon creates a negative volume inversion that can corrupt the entire level BSP tree.",
            tags="t3d_math,bsp_geometry,normal_vectors,coplanar_polys,watertight",
            author_reference="Tim Sweeney (Unreal Engine CSG Architecture)",
        )

        self.ingest_knowledge_entry(
            category="tips_and_tricks",
            title="🤖 Automated AI Reachability Lattice & Scout Simulation",
            summary="Procedurally synthesizes 100% connected Botpack reachability graphs with automatic Scout capsule clearance verification.",
            engine_target="UT99 / UE1 / UE2",
            step_by_step=[
                "1. Spacing Constraint: Place PathNodes with inter-node distance $d \\in [300, 650]\\text{ UU}$ across all traversable surfaces.",
                "2. Ground Elevation Offset: Always elevate PathNodes $Z_{\\text{floor}} + 30\\text{ UU}$ to avoid collision mesh clipping.",
                "3. Chokepoint Triad: In doorways, gates, and bridges, synthesize a 3-node sequence (Approach $\\to$ Threshold $\\to$ Exit).",
                "4. Scout Clearance: Verify cylinder radius $R=42\\text{ UU}$ and height $H=80\\text{ UU}$ have unobstructed line of sight.",
                "5. PlayerStart Spacing: Distribute PlayerStart spawns $\\ge 128\\text{ UU}$ apart with $+50\\text{ UU}$ ground clearance.",
            ],
            technical_trick="Never allow two PathNodes within 128 UU of each other; the path compiler will generate redundant zero-weight ReachSpecs.",
            tags="procedural_ai,pathnode_lattice,reachability,scout_clearance,botpack",
            author_reference="Steve Polge & UAH AI Engine",
        )

        self.ingest_knowledge_entry(
            category="engine_secrets",
            title="🌲 Procedural Foliage & Clustered Poisson Scattering",
            summary="Scatters dense natural outdoor vegetation (pines, plants, boulders) deterministically without exceeding actor memory budgets.",
            engine_target="UE1 / UT99 / UE2",
            step_by_step=[
                "1. Height-Bound Filtering: Scatter `UnrealShare.Tree1-6` across valley slopes and mountain ridges ($Z \\in [\\text{floor\\_z}, \\text{bluff\\_z} + 512]$).",
                "2. Riverbank Flora: Scatter `UnrealShare.Plant1-7` and `NaliFruit` within 512 UU of water channels.",
                "3. Slope Granite Boulders: Place `UnrealI.BigRock` and `UnrealShare.Boulder` at the base of vertical cliff cuts.",
                "4. Minimum Distance Exclusion: Maintain $\\ge 256\\text{ UU}$ spacing between trees to prevent bot path blockage.",
                "5. Collision Budgeting: Keep total interactive actor count under 384 actors (75% of the 512 network actor allocation).",
            ],
            technical_trick="Scatter trees with varying species index (`Tree1`, `Tree2`, `Tree3`, `Tree6`) to break visual tiling across expansive mountain vistas.",
            tags="procedural_foliage,poisson_scatter,tree_clustering,actor_budgeting",
            author_reference="UAH World Synthesis Standards",
        )

        logger.info("Master Curriculum seeding complete (36+ Master Lessons, Procedural Technologies, Illusions & Deconstructions).")

