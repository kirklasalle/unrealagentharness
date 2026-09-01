r"""
Persistent Long-Term Memory, Knowledge Base Indexer & Wisdom Engine.
Zero-dependency SQLite store for architectural insights, build telemetry, and dynamic RAG retrieval.
"""

import json
import os
import re
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from .logger import get_logger

logger = get_logger("MemoryEngine", "memory_engine.log")


class MemoryEngine:
    """Manages persistent SQLite memory, wisdom insights, telemetry, and dynamic knowledge base indexing."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            log_dir = base_dir / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = log_dir / "memory.db"

        self._init_db()
        self._seed_foundational_wisdom()
        self.seed_procedural_technology_graph()
        logger.info(f"MemoryEngine initialized with database at: '{self.db_path}'")


    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initializes tables for wisdom insights, build telemetry, knowledge base index, and session memory."""
        with self._connection() as conn:
            cursor = conn.cursor()

            # Wisdom & Architectural Insights
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wisdom_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    confidence REAL DEFAULT 1.0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    UNIQUE(category, title)
                )
            """)

            # Build Telemetry & History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS build_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    engine_id TEXT NOT NULL,
                    build_type TEXT NOT NULL,
                    command_count INTEGER DEFAULT 0,
                    entity_count INTEGER DEFAULT 0,
                    bounds_json TEXT DEFAULT '{}',
                    reachability_score REAL DEFAULT 1.0,
                    status TEXT DEFAULT 'success',
                    details TEXT DEFAULT '',
                    timestamp REAL NOT NULL
                )
            """)

            # Knowledge Base Documents Index (for dynamic retrieval)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    summary TEXT DEFAULT '',
                    content TEXT NOT NULL,
                    indexed_at REAL NOT NULL
                )
            """)

            # Session / Long-term Chat History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_executions_json TEXT DEFAULT '[]',
                    timestamp REAL NOT NULL
                )
            """)

            # Graph-shaped durable memory for reference artifacts, scene
            # graphs, build manifests, findings, and approvals.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_edges (
                    source_id TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    payload_json TEXT DEFAULT '{}',
                    created_at REAL NOT NULL,
                    PRIMARY KEY (source_id, relation, target_id)
                )
            """)

            conn.commit()

    def _seed_foundational_wisdom(self) -> None:
        """Seeds foundational architectural directives and crash-prevention wisdom."""
        seeds = [
            (
                "csg_math",
                "Watertight Brush & Coplanar Polygon Rule",
                "All CSG brush polygons must be strictly coplanar (Ax + By + Cz + D = 0) with clockwise vertex winding relative to outward surface normals. Non-coplanar quads cause BSP hole corruption.",
                "csg,geometry,bsp,t3d,winding",
            ),
            (
                "crash_mitigation",
                "UT2004 Navigation Crash Mitigation",
                "In Unreal Tournament 2004 (UE2.5), never invoke raw 'PATHS BUILD' via command line as FPathBuilder throws AIController GPFs. Always issue 'PATHS DEFINE' followed by FLUSH.",
                "ut2004,paths,crash,fpathbuilder,navigation",
            ),
            (
                "texture_pipeline",
                "Dynamic UTX Texture Package Preloading",
                "Always execute 'OBJ LOAD FILE=..\\Textures\\<pkg>.utx PACKAGE=<pkg>' before placing brushes to prevent polygons defaulting to flat grey or missing material placeholders.",
                "textures,utx,materials,obj_load,ue1,ue2",
            ),
            (
                "bot_pathing",
                "Zero Embedded Geometry PathNode Clearances",
                "Place PathNodes exactly 25 to 35 UU above floor geometry and ensure minimum 500-700 UU spacing. Floor-penetrating nodes break bot reachability lattices.",
                "pathing,ai,reachspec,pathnode,navigation",
            ),
            (
                "lighting",
                "8-bit HSV Unreal Color Radiosity",
                "In UE1/UE2.5, LightBrightness (120-220), LightRadius (32-64), LightHue (0-255: Red=0, Gold=35, Green=85, Cyan=145, Blue=170), and LightSaturation (0=Pure Vivid, 255=White Monochrome).",
                "lighting,radiosity,colors,hsv,atmosphere",
            ),
            (
                "csg_skybox",
                "Outdoor Skybox Projection & FakeBackdrop Rule",
                "Outdoor ceilings must be flagged with PF_FakeBackdrop | PF_Unlit (Flags=4194432) and accompanied by a thin SkyOpening subtract slab to guarantee the isolated SkyZoneInfo projects celestial horizons without opaque grey tiles.",
                "skybox,fakebackdrop,unlit,ceiling,flags,skyzone",
            ),
            (
                "civil_engineering",
                "Bedrock Grounding & Terrain Ramp Integration",
                "Never place additive architecture hovering over void. Always anchor fortresses and towers with solid bedrock bluffs, cliff skirts, and sloping terrain ramps connected to valley floor elevation.",
                "architecture,grounding,bluff,ramp,cliff,terrain",
            ),
            (
                "level_safety",
                "Chasm & River Gorge End-Cap Boundary Containment",
                "Subtracted river gorges and trenches must never terminate openly at world extents. Always seal both ends with solid rock end-cap blocking brushes (128-256 UU) to prevent player falls off the map.",
                "safety,gorge,river,bounds,void,fall,bsp",
            ),
            (
                "csg_detail",
                "Semi-Solid Architectural Enrichment (Zero BSP Cuts)",
                "Always generate decorative detail (merlons, buttresses, bridge arch ribs, stone piers, rock terraces) as semi-solid brushes (PF_Semisolid = 32). This maximizes visual fidelity within 75% engine budget without BSP cuts.",
                "semisolid,merlon,buttress,arch,pier,terrace,detail",
            ),
            (
                "fluid_rendering",
                "Translucent Waterfall Sheets & River Planes",
                "Waterfall sheets and river water planes must be flagged with PF_Translucent (4) | PF_Semisolid (32) = Flags=36 to ensure proper water depth rendering, buoyancy, and translucent cascade visuals.",
                "water,translucent,fluid,waterfall,river,semisolid",
            ),
            (
                "engine_internals",
                "UnLevel.h Actors(1) Builder Brush Invariant",
                "In Unreal Engine C++ architecture (UnLevel.h line 507: check(Actors(1)->Brush != NULL)), Actors(0) is strictly LevelInfo and Actors(1) is hardcoded as the active Builder Brush (CsgOper=CSG_Active). Monolithic T3D files must emit Brush0 as the second actor before all other geometry and non-brush entities to avoid engine assertion crashes.",
                "unlevel,actors,builder_brush,brush0,csg_active,assertion,crash,t3d",
            ),
        ]

        for cat, title, content, tags in seeds:
            self.record_wisdom(category=cat, title=title, content=content, tags=tags)

    # -------------------------------------------------------------------------
    # WISDOM MANAGEMENT & RETRIEVAL
    # -------------------------------------------------------------------------
    def record_wisdom(
        self,
        category: str,
        title: str,
        content: str,
        tags: str = "",
        confidence: float = 1.0,
    ) -> bool:
        """Records or updates an architectural insight or lesson in persistent memory."""
        now = time.time()
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO wisdom_insights (category, title, content, tags, confidence, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(category, title) DO UPDATE SET
                        content = excluded.content,
                        tags = excluded.tags,
                        confidence = excluded.confidence,
                        updated_at = excluded.updated_at
                """, (category, title, content, tags, confidence, now, now))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to record wisdom '{title}': {e}")
            return False

    def query_wisdom(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Queries stored wisdom insights matching keywords or categories."""
        tokens = [t.lower().strip() for t in re.split(r"\W+", query) if len(t) > 2]
        
        conditions = []
        params: List[Any] = []

        if tokens:
            token_conds = []
            for t in tokens[:4]:
                token_conds.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(category) LIKE ?)")
                p = f"%{t}%"
                params.extend([p, p, p, p])
            conditions.append(f"({' OR '.join(token_conds)})")

        if category:
            conditions.append("category LIKE ?")
            params.append(f"%{category}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        # Prefer exact title matches for focused operator queries, then fall
        # back to confidence and recency. This prevents foundational seed
        # entries from masking a newly recorded, exact user lesson.
        title_priority = "CASE WHEN LOWER(title) LIKE ? THEN 0 ELSE 1 END, " if tokens else ""
        if tokens:
            params.append(f"%{tokens[0]}%")
        sql = f"SELECT * FROM wisdom_insights {where_clause} ORDER BY {title_priority} confidence DESC, updated_at DESC LIMIT ?"
        params.append(limit)

        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error querying wisdom: {e}")
            return []

    # -------------------------------------------------------------------------
    # BUILD TELEMETRY RECORDING
    # -------------------------------------------------------------------------
    def record_build_event(
        self,
        engine_id: str,
        build_type: str,
        command_count: int = 0,
        entity_count: int = 0,
        bounds: Optional[Dict[str, Any]] = None,
        reachability_score: float = 1.0,
        status: str = "success",
        details: str = "",
    ) -> bool:
        """Logs a completed procedural build event into persistent telemetry."""
        now = time.time()
        bounds_json = json.dumps(bounds or {})
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO build_telemetry (
                        engine_id, build_type, command_count, entity_count,
                        bounds_json, reachability_score, status, details, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (engine_id, build_type, command_count, entity_count, bounds_json, reachability_score, status, details, now))
                conn.commit()
                logger.info(f"Recorded build telemetry: '{build_type}' on '{engine_id}' ({command_count} cmds)")
                return True
        except Exception as e:
            logger.error(f"Failed to record build event: {e}")
            return False

    def get_recent_builds(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recent build telemetry events."""
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM build_telemetry ORDER BY timestamp DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error retrieving build telemetry: {e}")
            return []

    # -------------------------------------------------------------------------
    # GRAPH MEMORY
    # -------------------------------------------------------------------------
    def record_graph_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Upserts a durable graph node without storing secret material."""
        now = time.time()
        try:
            with self._connection() as conn:
                conn.execute("""
                    INSERT INTO graph_nodes (id, node_type, label, payload_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        node_type = excluded.node_type,
                        label = excluded.label,
                        payload_json = excluded.payload_json,
                        updated_at = excluded.updated_at
                """, (node_id, node_type, label, json.dumps(payload or {}, sort_keys=True), now, now))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to record graph node '{node_id}': {e}")
            return False

    def record_graph_edge(
        self,
        source_id: str,
        relation: str,
        target_id: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Upserts a typed relationship between durable graph nodes."""
        try:
            with self._connection() as conn:
                conn.execute("""
                    INSERT INTO graph_edges (source_id, relation, target_id, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(source_id, relation, target_id) DO UPDATE SET
                        payload_json = excluded.payload_json
                """, (source_id, relation, target_id, json.dumps(payload or {}, sort_keys=True), time.time()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to record graph edge '{source_id}' -[{relation}]-> '{target_id}': {e}")
            return False

    def query_graph(self, query: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """Returns graph nodes matching a label/type/payload text query."""
        pattern = f"%{query.lower()}%"
        try:
            with self._connection() as conn:
                rows = conn.execute("""
                    SELECT id, node_type, label, payload_json, created_at, updated_at
                    FROM graph_nodes
                    WHERE LOWER(id) LIKE ? OR LOWER(node_type) LIKE ?
                       OR LOWER(label) LIKE ? OR LOWER(payload_json) LIKE ?
                    ORDER BY updated_at DESC LIMIT ?
                """, (pattern, pattern, pattern, pattern, limit)).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to query graph memory: {e}")
            return []

    def record_reference_analysis(
        self,
        scene_id: str,
        source_path: str,
        scene_graph_path: str,
        source_sha256: str,
        landmark_count: int,
    ) -> bool:
        """Persists a reference-analysis result and its artifact relationships."""
        source_id = f"artifact:{source_sha256}"
        graph_id = f"scene-graph:{scene_id}"
        ok = self.record_graph_node(
            source_id,
            "artifact",
            Path(source_path).name,
            {"path": source_path, "sha256": source_sha256, "artifact_kind": "reference_image"},
        )
        ok = self.record_graph_node(
            graph_id,
            "scene",
            scene_id,
            {
                "scene_graph_path": scene_graph_path,
                "source_sha256": source_sha256,
                "landmark_count": landmark_count,
                "analysis_schema": "uah.valley_scene_graph.v1",
            },
        ) and ok
        return self.record_graph_edge(source_id, "derived_to", graph_id) and ok

    def record_artifact(
        self,
        artifact_id: str,
        path: str,
        kind: str,
        size: int,
        sha256: str,
    ) -> bool:
        """Stores a chat artifact node for future retrieval and audit."""
        return self.record_graph_node(
            f"artifact:{artifact_id}",
            "artifact",
            Path(path).name,
            {"path": path, "kind": kind, "size": size, "sha256": sha256},
        )

    def record_build_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Persists a build manifest node for future diagnosis and retrieval."""
        build_id = str(manifest.get("build_id", f"build-{int(time.time())}"))
        ok = self.record_graph_node(
            f"build:{build_id}", "build", build_id,
            {key: value for key, value in manifest.items() if key not in {"api_key", "token", "secret"}},
        )
        scene_path = manifest.get("scene_graph_path")
        if scene_path:
            ok = self.record_graph_edge(f"build:{build_id}", "uses_scene_graph", f"scene-graph:{Path(scene_path).stem}") and ok
        return ok

    def record_build_finding(self, build_id: str, finding_type: str, message: str, confidence: float = 1.0) -> bool:
        """Stores a build finding and links it to a build node."""
        finding_id = f"finding:{build_id}:{finding_type}:{abs(hash(message))}"
        ok = self.record_graph_node(
            finding_id,
            "finding",
            finding_type,
            {"message": message, "confidence": confidence, "build_id": build_id},
        )
        return self.record_graph_edge(f"build:{build_id}", "has_finding", finding_id) and ok

    def seed_procedural_technology_graph(self) -> None:

        """Seeds the permanent Graph Memory with the complete distilled Unreal Procedural Technology ontology."""
        nodes = [
            (
                "procedural:pcg_csg_stack",
                "procedural_technology",
                "Hierarchical CSG Stack (Macro-to-Micro Decomposition)",
                {
                    "paradigm": "subtractive_macro_to_semisolid_micro",
                    "layers": [
                        "1_subtractive_master_hull",
                        "2_additive_bedrock_foundations",
                        "3_subtractive_negative_spaces",
                        "4_semisolid_detail_multipliers",
                        "5_nonsolid_translucent_projections",
                    ],
                    "budget_limit_pct": 0.75,
                },
            ),
            (
                "procedural:watertight_bsp_math",
                "csg_rule",
                "Watertight BSP Mathematical Plane Equations",
                {
                    "plane_equation": "Ax + By + Cz + D = 0",
                    "winding_order": "clockwise_outward_normals",
                    "non_planar_triangulation": "split_into_coplanar_triangles",
                    "zero_hom_guarantee": True,
                },
            ),
            (
                "procedural:stepped_terrain_heightfield",
                "terrain_rule",
                "Procedural Heightfield & Stepped Outdoor Terrain in CSG",
                {
                    "features": ["beveled_terraces", "interlocking_ramps", "subtracted_river_chasms", "rock_faceting"],
                    "floor_material": "GenEarth.grasrok2",
                    "cliff_material": "GenEarth.Rockfac1",
                },
            ),
            (
                "procedural:atmospheric_radiosity_lighting",
                "lighting_rule",
                "Dual-Spectrum Complementary Atmospheric Radiosity",
                {
                    "key_light": {"hue": 38, "saturation": 100, "brightness": 250, "type": "warm_sun_torch"},
                    "fill_light": {"hue": 155, "saturation": 160, "brightness": 180, "type": "cool_sky_water_bounce"},
                    "dynamic_fx": ["LE_WateryShimmer", "LE_TorchWaver"],
                },
            ),
            (
                "procedural:ai_reachability_lattice",
                "navigation_rule",
                "Automated AI Reachability Lattice & Scout Clearance",
                {
                    "node_spacing_range": [300, 650],
                    "floor_elevation_offset": 30.0,
                    "scout_collision_cylinder": {"radius": 42.0, "height": 80.0},
                    "chokepoint_triad": ["approach", "threshold", "exit"],
                },
            ),
            (
                "procedural:celestial_skybox_parallax",
                "skybox_rule",
                "Isolated Parallax Skybox Chamber & FakeBackdrop Projection",
                {
                    "chamber_dimension": [1024, 1024, 1024],
                    "actor": "Engine.SkyZoneInfo",
                    "surface_flag": 4194432,  # PF_FakeBackdrop | PF_Unlit
                    "parallax_scale": "infinite",
                },
            ),
            (
                "procedural:poisson_foliage_scattering",
                "foliage_rule",
                "Procedural Foliage & Clustered Poisson Scatter",
                {
                    "species": ["UnrealShare.Tree1", "Tree2", "Tree3", "Tree6", "Plant1-7", "BigRock", "Boulder"],
                    "min_tree_spacing": 256.0,
                    "max_interactive_actors": 384,
                },
            ),
        ]

        edges = [
            ("procedural:pcg_csg_stack", "implements_rule", "procedural:watertight_bsp_math"),
            ("procedural:pcg_csg_stack", "governs_generation", "skill:valley_fortress_synthesis"),
            ("procedural:stepped_terrain_heightfield", "derived_to", "skill:valley_fortress_synthesis"),
            ("procedural:atmospheric_radiosity_lighting", "illuminates_scene", "skill:valley_fortress_synthesis"),
            ("procedural:celestial_skybox_parallax", "projects_vista_for", "skill:valley_fortress_synthesis"),
            ("procedural:ai_reachability_lattice", "pathfinds_map", "skill:valley_fortress_synthesis"),
            ("procedural:poisson_foliage_scattering", "populates_terrain", "skill:valley_fortress_synthesis"),
            ("skill:unrealed_viewport_setup", "inspects_geometry", "procedural:pcg_csg_stack"),
        ]

        for node_id, node_type, label, payload in nodes:
            self.record_graph_node(node_id, node_type, label, payload)

        for source_id, relation, target_id in edges:
            self.record_graph_edge(source_id, relation, target_id)

        logger.info(f"Graph Memory seeded with {len(nodes)} procedural technology nodes and {len(edges)} semantic edges.")



    # -------------------------------------------------------------------------
    # DYNAMIC KNOWLEDGE BASE INDEXING (RAG)
    # -------------------------------------------------------------------------
    def index_documentation_directory(self, docs_dir: Optional[str] = None) -> int:
        """Scans and indexes Markdown documents in docs/ directory for fast semantic retrieval."""
        if docs_dir:
            target_dir = Path(docs_dir)
        else:
            target_dir = Path(__file__).resolve().parent.parent / "docs"

        if not target_dir.exists():
            logger.warning(f"Docs directory not found: {target_dir}")
            return 0

        indexed_count = 0
        now = time.time()

        for md_file in target_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else md_file.stem

                # Extract first paragraph as summary
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.strip().startswith("#")]
                summary = paragraphs[0][:300] if paragraphs else ""

                category = "guide"
                if "AUDIT" in md_file.name.upper():
                    category = "audit"
                elif "SPECIFICATION" in md_file.name.upper():
                    category = "specification"
                elif "REFERENCE" in md_file.name.upper():
                    category = "reference"
                elif "KNOWLEDGEBASE" in md_file.name.upper():
                    category = "knowledgebase"

                with self._connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO knowledge_documents (file_path, title, category, summary, content, indexed_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(file_path) DO UPDATE SET
                            title = excluded.title,
                            category = excluded.category,
                            summary = excluded.summary,
                            content = excluded.content,
                            indexed_at = excluded.indexed_at
                    """, (str(md_file), title, category, summary, content, now))
                    conn.commit()
                    indexed_count += 1
            except Exception as e:
                logger.error(f"Error indexing doc file '{md_file.name}': {e}")

        logger.info(f"Indexed {indexed_count} knowledge base documents into memory database.")
        return indexed_count

    def search_knowledge_base(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Searches indexed documentation for relevant excerpts matching a user concept."""
        tokens = [t.lower().strip() for t in re.split(r"\W+", query) if len(t) > 2]
        if not tokens:
            return []

        conditions = []
        params: List[Any] = []
        for t in tokens[:4]:
            conditions.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ? OR LOWER(summary) LIKE ?)")
            p = f"%{t}%"
            params.extend([p, p, p])

        sql = f"SELECT id, file_path, title, category, summary FROM knowledge_documents WHERE {' OR '.join(conditions)} LIMIT ?"
        params.append(limit)

        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    # -------------------------------------------------------------------------
    # CONTEXT AUGMENTATION
    # -------------------------------------------------------------------------
    def build_augmented_context(self, user_query: str, engine_id: str) -> str:
        """Retrieves and formats relevant wisdom insights and documentation notes for injection into LLM prompts."""
        wisdom_items = self.query_wisdom(f"{engine_id} {user_query}", limit=3)
        doc_items = self.search_knowledge_base(user_query, limit=2)

        directives = []
        if wisdom_items:
            directives.append("RETRIEVED ARCHITECTURAL WISDOM:")
            for w in wisdom_items:
                directives.append(f"• [{w['category'].upper()}] {w['title']}: {w['content']}")

        if doc_items:
            directives.append("\nREFERENCED KNOWLEDGE BASE ARTICLES:")
            for d in doc_items:
                directives.append(f"• {d['title']} ({d['category']}): {d['summary']}")

        return "\n".join(directives) if directives else ""
