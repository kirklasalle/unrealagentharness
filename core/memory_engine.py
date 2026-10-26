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
        self.seed_universal_knowledge_system()
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
    # UNIVERSAL KNOWLEDGE SYSTEM (UKS) COGNITIVE GRAPH ENGINE
    # -------------------------------------------------------------------------
    def uks_register_concept(
        self,
        concept_id: str,
        category: str,
        label: str,
        attributes: Optional[Dict[str, Any]] = None,
        parents: Optional[List[str]] = None,
        relations: Optional[List[Tuple[str, str, Dict[str, Any]]]] = None,
        confidence: float = 1.0,
    ) -> bool:
        """Registers a concept node into UKS memory with taxonomy and relational links."""
        payload = dict(attributes or {})
        payload["confidence"] = confidence
        payload["uks_category"] = category
        if parents:
            payload["parents"] = parents

        ok = self.record_graph_node(concept_id, category, label, payload)

        if parents:
            for p_id in parents:
                ok = self.record_graph_edge(concept_id, "subclass_of", p_id) and ok

        if relations:
            for rel, target_id, edge_payload in relations:
                ok = self.record_graph_edge(concept_id, rel, target_id, edge_payload) and ok

        return ok

    def uks_link_concepts(
        self,
        source_id: str,
        relation: str,
        target_id: str,
        weight: float = 1.0,
        payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Links two concepts with a typed semantic relation and weight."""
        edge_data = dict(payload or {})
        edge_data["weight"] = weight
        return self.record_graph_edge(source_id, relation, target_id, edge_data)

    def uks_get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single concept node with its attributes, parents, children, and edges."""
        try:
            with self._connection() as conn:
                node_row = conn.execute(
                    "SELECT id, node_type, label, payload_json, created_at, updated_at FROM graph_nodes WHERE id = ?",
                    (concept_id,),
                ).fetchone()
                if not node_row:
                    return None

                node = dict(node_row)
                node["attributes"] = json.loads(node.get("payload_json", "{}"))

                # Outgoing edges
                out_rows = conn.execute(
                    "SELECT relation, target_id, payload_json FROM graph_edges WHERE source_id = ?",
                    (concept_id,),
                ).fetchall()
                node["out_edges"] = [
                    {"relation": r["relation"], "target_id": r["target_id"], "payload": json.loads(r["payload_json"] or "{}")}
                    for r in out_rows
                ]

                # Incoming edges
                in_rows = conn.execute(
                    "SELECT source_id, relation, payload_json FROM graph_edges WHERE target_id = ?",
                    (concept_id,),
                ).fetchall()
                node["in_edges"] = [
                    {"source_id": r["source_id"], "relation": r["relation"], "payload": json.loads(r["payload_json"] or "{}")}
                    for r in in_rows
                ]

                # Taxonomy
                node["parents"] = [e["target_id"] for e in node["out_edges"] if e["relation"] in ("subclass_of", "is_a")]
                node["children"] = [e["source_id"] for e in node["in_edges"] if e["relation"] in ("subclass_of", "is_a")]

                return node
        except Exception as e:
            logger.error(f"Error retrieving UKS concept '{concept_id}': {e}")
            return None

    def uks_traverse_graph(
        self,
        start_id: str,
        max_depth: int = 2,
        relation_filter: Optional[List[str]] = None,
        direction: str = "both",
    ) -> Dict[str, Any]:
        """Breadth-first graph traversal returning a connected subgraph around a concept."""
        visited_nodes: set = set()
        collected_nodes: Dict[str, Dict[str, Any]] = {}
        collected_edges: List[Dict[str, Any]] = []

        queue = [(start_id, 0)]
        visited_nodes.add(start_id)

        try:
            with self._connection() as conn:
                while queue:
                    curr_id, depth = queue.pop(0)

                    nrow = conn.execute(
                        "SELECT id, node_type, label, payload_json FROM graph_nodes WHERE id = ?",
                        (curr_id,),
                    ).fetchone()
                    if nrow:
                        collected_nodes[curr_id] = {
                            "id": nrow["id"],
                            "node_type": nrow["node_type"],
                            "label": nrow["label"],
                            "attributes": json.loads(nrow["payload_json"] or "{}"),
                            "depth": depth,
                        }

                    if depth >= max_depth:
                        continue

                    # Outgoing edges
                    if direction in ("out", "both"):
                        out_edges = conn.execute(
                            "SELECT relation, target_id, payload_json FROM graph_edges WHERE source_id = ?",
                            (curr_id,),
                        ).fetchall()
                        for edge in out_edges:
                            rel = edge["relation"]
                            tgt = edge["target_id"]
                            if relation_filter and rel not in relation_filter:
                                continue
                            collected_edges.append({
                                "source_id": curr_id,
                                "relation": rel,
                                "target_id": tgt,
                                "payload": json.loads(edge["payload_json"] or "{}"),
                            })
                            if tgt not in visited_nodes:
                                visited_nodes.add(tgt)
                                queue.append((tgt, depth + 1))

                    # Incoming edges
                    if direction in ("in", "both"):
                        in_edges = conn.execute(
                            "SELECT source_id, relation, payload_json FROM graph_edges WHERE target_id = ?",
                            (curr_id,),
                        ).fetchall()
                        for edge in in_edges:
                            rel = edge["relation"]
                            src = edge["source_id"]
                            if relation_filter and rel not in relation_filter:
                                continue
                            collected_edges.append({
                                "source_id": src,
                                "relation": rel,
                                "target_id": curr_id,
                                "payload": json.loads(edge["payload_json"] or "{}"),
                            })
                            if src not in visited_nodes:
                                visited_nodes.add(src)
                                queue.append((src, depth + 1))

            return {
                "root_id": start_id,
                "node_count": len(collected_nodes),
                "edge_count": len(collected_edges),
                "nodes": list(collected_nodes.values()),
                "edges": collected_edges,
            }
        except Exception as e:
            logger.error(f"Error traversing UKS graph from '{start_id}': {e}")
            return {"root_id": start_id, "node_count": 0, "edge_count": 0, "nodes": [], "edges": []}

    def uks_query_neighborhood(self, concept_id: str, hops: int = 1) -> Dict[str, Any]:
        """Returns the immediate semantic neighborhood around a UKS concept."""
        return self.uks_traverse_graph(concept_id, max_depth=hops, direction="both")

    def uks_infer_properties(self, concept_id: str) -> Dict[str, Any]:
        """Infers effective attributes by climbing the taxonomy tree (subclass_of / is_a)."""
        visited: set = set()
        aggregated_props: Dict[str, Any] = {}
        queue = [concept_id]

        try:
            with self._connection() as conn:
                while queue:
                    curr = queue.pop(0)
                    if curr in visited:
                        continue
                    visited.add(curr)

                    nrow = conn.execute("SELECT payload_json FROM graph_nodes WHERE id = ?", (curr,)).fetchone()
                    if nrow:
                        attrs = json.loads(nrow["payload_json"] or "{}")
                        for k, v in attrs.items():
                            if k not in aggregated_props:
                                aggregated_props[k] = v

                    parents = conn.execute(
                        "SELECT target_id FROM graph_edges WHERE source_id = ? AND relation IN ('subclass_of', 'is_a')",
                        (curr,),
                    ).fetchall()
                    for p in parents:
                        if p["target_id"] not in visited:
                            queue.append(p["target_id"])

            return aggregated_props
        except Exception as e:
            logger.error(f"Error inferring UKS properties for '{concept_id}': {e}")
            return {}

    def uks_validate_constraints(self, action_type: str, entity_props: Dict[str, Any]) -> Dict[str, Any]:
        """Validates procedural actions against the UKS cognitive constraint graph."""
        violations = []
        recommendations = []

        # 1. 75% Engine Budget Law Validation
        brush_count = entity_props.get("brush_count", 0)
        actor_count = entity_props.get("actor_count", 0)
        if brush_count > 300:
            violations.append(f"Brush count {brush_count} exceeds recommended per-wing budget (300 brushes).")
            recommendations.append("Convert decorative trim and pillars to semi-solid (PF_Semisolid=32) to avoid BSP cuts.")

        if actor_count > 500:
            violations.append(f"Actor count {actor_count} exceeds 75% engine budget threshold.")
            recommendations.append("Consolidate pathing lattice to 500-700 UU spacing and prune excess inventory spot markers.")

        # 2. Coplanar geometry & winding validation
        if entity_props.get("coplanar") is False:
            violations.append("Non-coplanar polygon detected. Violates watertight CSG plane equation Ax + By + Cz + D = 0.")
            recommendations.append("Split quad polygon into two coplanar triangles along diagonal to prevent HOM.")

        # 3. PathNode floor clearance
        elevation_offset = entity_props.get("floor_offset_uu", 30)
        if elevation_offset < 20 or elevation_offset > 50:
            violations.append(f"PathNode floor clearance ({elevation_offset} UU) outside golden range [20, 50] UU.")
            recommendations.append("Set PathNode Z offset strictly to +30 UU above walkable terrain.")

        # 4. Outdoor ceiling FakeBackdrop
        if entity_props.get("is_outdoor") and not entity_props.get("fake_backdrop"):
            violations.append("Outdoor environment missing PF_FakeBackdrop flag on celestial sky portal.")
            recommendations.append("Apply PF_FakeBackdrop (Flags=4194432) to ceiling polygons and spawn SkyZoneInfo in isolated 1024^3 skybox.")

        return {
            "valid": len(violations) == 0,
            "action_type": action_type,
            "violations": violations,
            "recommendations": recommendations,
        }

    def uks_export_jsonld(self, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Exports the UKS graph memory as a standard JSON-LD semantic knowledge graph."""
        try:
            with self._connection() as conn:
                where_clause = "WHERE node_type = ?" if category_filter else ""
                params = (category_filter,) if category_filter else ()
                nodes = conn.execute(f"SELECT id, node_type, label, payload_json FROM graph_nodes {where_clause}", params).fetchall()

                graph_entries = []
                for n in nodes:
                    attrs = json.loads(n["payload_json"] or "{}")
                    entry = {
                        "@id": n["id"],
                        "@type": n["node_type"],
                        "label": n["label"],
                        **attrs,
                    }
                    edges = conn.execute(
                        "SELECT relation, target_id, payload_json FROM graph_edges WHERE source_id = ?",
                        (n["id"],),
                    ).fetchall()
                    for edge in edges:
                        rel = edge["relation"]
                        tgt = edge["target_id"]
                        if rel not in entry:
                            entry[rel] = tgt
                        elif isinstance(entry[rel], list):
                            entry[rel].append(tgt)
                        else:
                            entry[rel] = [entry[rel], tgt]
                    graph_entries.append(entry)

                return {
                    "@context": {
                        "uks": "https://unrealagentharness.com/schema/uks#",
                        "subclass_of": {"@id": "http://www.w3.org/2000/01/rdf-schema#subClassOf", "@type": "@id"},
                        "is_a": {"@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "@type": "@id"},
                        "part_of": {"@id": "http://purl.obolibrary.org/obo/BFO_0000050", "@type": "@id"},
                    },
                    "@graph": graph_entries,
                }
        except Exception as e:
            logger.error(f"Error exporting UKS JSON-LD: {e}")
            return {"@context": {}, "@graph": []}

    def seed_universal_knowledge_system(self) -> None:
        """Seeds the Universal Knowledge System (UKS) ontology across Architecture, 3D/Animation, Textures, and UnrealEd."""
        concepts = [
            # -----------------------------------------------------------------
            # 1. Architectural Engineering Ontologies
            # -----------------------------------------------------------------
            (
                "uks:arch:classical_order",
                "architecture",
                "Classical Architectural Order (Antiquity Foundation)",
                {
                    "canon": "Vitruvian / Vignola",
                    "principles": ["symmetry", "entablature_proportions", "fluted_shafts", "stylobate_elevation"],
                    "structural_role": "compression_load_bearing",
                },
                None,
            ),
            (
                "uks:arch:doric_order",
                "architecture",
                "Doric Architectural Order",
                {
                    "column_ratio": "1:8",
                    "capital": "plain_circular_echinus",
                    "entablature": "triglyphs_and_metopes",
                    "spatial_use": "monumental_fortress_temples",
                },
                ["uks:arch:classical_order"],
            ),
            (
                "uks:arch:ionic_order",
                "architecture",
                "Ionic Architectural Order",
                {
                    "column_ratio": "1:9",
                    "capital": "scroll_like_volutes",
                    "entablature": "dentil_cornice_frieze",
                    "spatial_use": "civic_libraries_and_sanctuaries",
                },
                ["uks:arch:classical_order"],
            ),
            (
                "uks:arch:corinthian_order",
                "architecture",
                "Corinthian Architectural Order",
                {
                    "column_ratio": "1:10",
                    "capital": "ornate_carved_acanthus_leaves",
                    "entablature": "decorative_modillion_cornice",
                    "spatial_use": "grand_imperial_throne_rooms",
                },
                ["uks:arch:classical_order"],
            ),
            (
                "uks:arch:gothic_grammar",
                "architecture",
                "Gothic Structural Engineering Grammar",
                {
                    "core_invention": "skeletal_framework_with_concentrated_thrust",
                    "structural_trio": ["pointed_arch", "ribbed_vault", "flying_buttress"],
                    "spatial_effect": "verticality_and_weightless_illumination",
                },
                None,
            ),
            (
                "uks:arch:pointed_arch",
                "architecture",
                "Gothic Pointed Arch (Equilateral & Lancet)",
                {
                    "thrust_vector": "reduced_lateral_shear_increased_vertical",
                    "csg_profile": "two_intersecting_arc_quadrants",
                    "height_to_width": "2:1",
                },
                ["uks:arch:gothic_grammar"],
            ),
            (
                "uks:arch:ribbed_vault",
                "architecture",
                "Gothic Ribbed Groin Vault",
                {
                    "components": ["transverse_ribs", "diagonal_ogive_ribs", "web_infill"],
                    "csg_construction": "subtracted_diagonals_with_semisolid_rib_moldings",
                },
                ["uks:arch:gothic_grammar"],
            ),
            (
                "uks:arch:flying_buttress",
                "architecture",
                "Exterior Flying Buttress & Flyer Arch",
                {
                    "function": "transmits_outward_roof_thrust_across_aisle_to_heavy_pier",
                    "pinnacle_weight": "downward_compression_anchors_pier",
                },
                ["uks:arch:gothic_grammar"],
            ),
            (
                "uks:arch:medieval_fortress",
                "architecture",
                "Medieval Military Fortification Topology",
                {
                    "defensive_layers": ["moat", "outer_curtain_wall", "barbican", "inner_keep", "bastions"],
                    "doctrine": "defense_in_depth_and_enfilade_crossfire",
                },
                None,
            ),
            (
                "uks:arch:curtain_wall",
                "architecture",
                "Defensive Stone Curtain Wall",
                {
                    "thickness_uu": 128.0,
                    "height_uu": 512.0,
                    "foundation": "anchored_into_granite_bedrock",
                    "allure_walkway_uu": 64.0,
                },
                ["uks:arch:medieval_fortress"],
            ),
            (
                "uks:arch:bastion_tower",
                "architecture",
                "Octagonal Flanking Bastion Tower",
                {
                    "geometry": "8_sided_extrusion",
                    "overlook_angle_deg": 360,
                    "eliminates_dead_ground": True,
                },
                ["uks:arch:medieval_fortress"],
            ),
            (
                "uks:arch:gatehouse_barbican",
                "architecture",
                "Fortified Gatehouse & Barbican Chokepoint",
                {
                    "features": ["portcullis_slot", "murder_holes", "double_drawbridge", "arrow_slits"],
                    "ai_pathing": "chokepoint_triad_with_high_priority_combat_spawns",
                },
                ["uks:arch:medieval_fortress"],
            ),
            (
                "uks:arch:scifi_brutalism",
                "architecture",
                "Sci-Fi Industrial Brutalism",
                {
                    "aesthetic": "exposed_reinforced_concrete_heavy_steel_bulkheads",
                    "motifs": ["cantilever_hangars", "conduit_galleries", "hexagonal_blast_doors"],
                    "lighting": "recessed_strip_lighting_and_pulsing_status_strobe",
                },
                None,
            ),
            (
                "uks:arch:spatial_sightlines",
                "architecture",
                "Multi-Tier Spatial Sightlines & Chokepoint Triad",
                {
                    "triad_stages": ["approach_zone", "threshold_bottleneck", "exit_distribution"],
                    "perch_elevation_uu": 256.0,
                    "dais_height_uu": 32.0,
                },
                None,
            ),

            # -----------------------------------------------------------------
            # 2. 3D Development & Animation Ontologies
            # -----------------------------------------------------------------
            (
                "uks:3d:csg_bsp_math",
                "3d_animation",
                "Watertight CSG & Binary Space Partitioning Math",
                {
                    "plane_equation": "Ax + By + Cz + D = 0",
                    "normal_computation": "(v1 - v0) cross (v2 - v0)",
                    "winding_rule": "clockwise_viewed_from_exterior",
                    "triangulation": "split_nonplanar_quads_at_diagonal",
                },
                None,
            ),
            (
                "uks:3d:skeletal_mesh",
                "3d_animation",
                "Skeletal Mesh & Hierarchical Bone Rigging",
                {
                    "engine_evolution": "UE2.0_through_UE5",
                    "features": ["hierarchical_bone_transforms", "dual_quaternion_blending", "vertex_skin_weights"],
                    "formats": [".psk", ".psa", ".fbx"],
                },
                None,
            ),
            (
                "uks:3d:vertex_animation",
                "3d_animation",
                "Vertex Animation Morphing (Unreal 1 Classic)",
                {
                    "engine": "UE1_namesake_and_UT99",
                    "method": "per_frame_vertex_coordinate_interpolation",
                    "formats": ["_d.3d", "_a.3d"],
                    "zero_matrix_overhead": True,
                },
                None,
            ),
            (
                "uks:3d:lod_cascade",
                "3d_animation",
                "Continuous Level of Detail (LOD) Simplification",
                {
                    "hysteresis": "screen_space_percentage_thresholds",
                    "transition": "dithered_crossfade_or_discrete_pop",
                    "budget_preservation": "keeps_viewport_framerate_pinned_at_solid_fps",
                },
                None,
            ),
            (
                "uks:3d:collision_hull",
                "3d_animation",
                "Collision Hull Primitives & Geometry Probes",
                {
                    "player_scout_cylinder": {"radius": 42.0, "height": 80.0},
                    "types": ["cylinder", "axis_aligned_box", "oriented_bounding_box", "discrete_oriented_polytope"],
                    "zero_complex_poly_in_ue1": True,
                },
                None,
            ),
            (
                "uks:3d:karma_physics",
                "3d_animation",
                "Karma Physics Engine & Ragdoll Dynamics (UE2.5)",
                {
                    "engine": "Unreal Tournament 2004",
                    "actors": ["KarmaActor", "KConstraint", "KHinge", "KCarWheelJoint"],
                    "ragdoll": "KMakeRagdoll_on_player_death",
                },
                None,
            ),
            (
                "uks:3d:matinee_cinematic",
                "3d_animation",
                "Matinee & Cinematic Sequence Interpolation",
                {
                    "features": ["spline_camera_paths", "fov_keyframing", "actor_director_tracks"],
                    "actors": ["InterpolationPoint", "InterpolatingActor"],
                },
                None,
            ),

            # -----------------------------------------------------------------
            # 3. Texture Development & Materials Ontologies
            # -----------------------------------------------------------------
            (
                "uks:mat:pbr_workflow",
                "texture_material",
                "Physically Based Rendering (PBR) Metallic-Roughness",
                {
                    "channels": ["Albedo", "Normal", "Roughness", "Metallic", "AmbientOcclusion", "Height"],
                    "energy_conservation": True,
                    "dielectric_f0": 0.04,
                },
                None,
            ),
            (
                "uks:mat:utx_package_architecture",
                "texture_material",
                "Unreal Stock UTX Texture Package Container",
                {
                    "file_extension": ".utx",
                    "loading_command": "OBJ LOAD FILE=..\\Textures\\<pkg>.utx PACKAGE=<pkg>",
                    "canonical_packages": [
                        "GenEarth.utx", "NaliCast.utx", "Ancient.utx", "ShaneSky.utx",
                        "UTtech1.utx", "UTtech2.utx", "Coret_FX.utx", "SpaceFX.utx", "Starship.utx"
                    ],
                },
                None,
            ),
            (
                "uks:mat:procedural_noise_shaders",
                "texture_material",
                "In-Engine Procedural Noise & Animated Textures",
                {
                    "classes": ["FireTexture", "WaterTexture", "WaveTexture", "WetTexture", "IceTexture"],
                    "realtime_generation": "cpu_perlin_and_cellular_cellular_automata",
                    "fx": ["flowing_waterfalls", "flickering_hearth_flames", "dynamic_plasma"],
                },
                None,
            ),
            (
                "uks:mat:uv_unwrapping",
                "texture_material",
                "Texel Density & Mathematical UV Coordinate Mapping",
                {
                    "standard_density": "1_texel_per_uu_or_256x256_per_256uu",
                    "alignment_commands": ["POLY TILING", "POLY ALIGN PLANAR", "POLY ALIGN WALLDIRECTION"],
                    "lightmap_density_ratio": "16:1",
                },
                None,
            ),
            (
                "uks:mat:compression_algorithms",
                "texture_material",
                "S3TC Texture Block Compression (DXT1 - DXT5 & BCn)",
                {
                    "dxt1": "4x4_block_color_1bit_punchthrough_alpha_8to1_compression",
                    "dxt3": "4x4_block_explicit_4bit_alpha_for_sharp_edges",
                    "dxt5": "4x4_block_interpolated_alpha_for_smooth_gradients",
                    "bcn": "modern_bc1_through_bc7_for_ue5_hdr",
                },
                None,
            ),

            # -----------------------------------------------------------------
            # 4. Advanced Unreal Editing Techniques & Skills
            # -----------------------------------------------------------------
            (
                "uks:ued:semisolid_brush",
                "unrealed_technique",
                "Semi-Solid Detail Brush (PF_Semisolid = 32)",
                {
                    "flags": 32,
                    "rule": "never_cuts_bsp_node_tree",
                    "usage": ["pillars", "merlons", "buttresses", "cornice_moldings", "stairs"],
                    "budget_benefit": "zero_bsp_splits_prevents_65k_node_gpf",
                },
                None,
            ),
            (
                "uks:ued:poly_flags_catalog",
                "unrealed_technique",
                "Unreal Poly Flags Mathematical Bitmask Catalog",
                {
                    "PF_Invisible": 1,
                    "PF_Masked": 2,
                    "PF_Translucent": 4,
                    "PF_NotSolid": 8,
                    "PF_Semisolid": 32,
                    "PF_Modulated": 64,
                    "PF_FakeBackdrop": 4194304,
                    "PF_TwoSided": 256,
                    "PF_Portal": 67108864,
                    "PF_Antiportal": 134217728,
                    "PF_Unlit": 4194432,
                },
                None,
            ),
            (
                "uks:ued:zone_portals",
                "unrealed_technique",
                "Zone Portals & Room BSP Occlusion Partitioning",
                {
                    "flag": 67108864,  # PF_Portal
                    "geometry": "2d_sheet_covering_doorways_and_hallway_apertures",
                    "actors": ["ZoneInfo", "WaterZone", "LavaZone", "VacuumZone"],
                    "occlusion_gain": "drastically_reduces_drawn_polys",
                },
                None,
            ),
            (
                "uks:ued:warp_zones",
                "unrealed_technique",
                "WarpZones (Seamless Non-Euclidean Spatial Teleporters)",
                {
                    "actors": ["WarpZoneInfo", "WarpZoneMarker"],
                    "perspective": "continuous_matrix_raytrace_through_portal",
                    "uses": ["infinite_hallways", "impossible_geometry", "orbital_elevator_links"],
                },
                None,
            ),
            (
                "uks:ued:skybox_parallax",
                "unrealed_technique",
                "Isolated Parallax Skybox Chamber & 1:16 Scale Horizon",
                {
                    "chamber_size_uu": [1024, 1024, 1024],
                    "anchor_actor": "Engine.SkyZoneInfo",
                    "portal_flag": 4194432,  # PF_FakeBackdrop | PF_Unlit
                    "projection": "infinite_depth_perspective_without_bsp_seam",
                },
                None,
            ),
            (
                "uks:ued:2d_shape_editor",
                "unrealed_technique",
                "2D Shape Editor Architectural Contours",
                {
                    "operations": ["Sheet_Sweep", "Linear_Extrude", "Revolve_360", "Bezier_Segment_Subdivision"],
                    "shapes": ["fluted_columns", "vault_arches", "curved_cornices", "pipe_elbows"],
                },
                None,
            ),
            (
                "uks:ued:brush_clipping",
                "unrealed_technique",
                "Brush 2D Planar Clipping & Splitting",
                {
                    "method": "define_2_or_3_points_on_viewport_then_clip",
                    "modes": ["CLIP_SPLIT", "CLIP_DELETE", "CLIP_FLIP"],
                    "preserves_topology": True,
                },
                None,
            ),
            (
                "uks:ued:intersect_deintersect",
                "unrealed_technique",
                "Intersect & De-intersect Boolean Geometry Carving",
                {
                    "intersect": "trims_builder_brush_to_contents_of_existing_world",
                    "deintersect": "trims_builder_brush_to_void_of_existing_world",
                    "workflow": "carve_complex_composite_sculptures_and_spiral_stairwells",
                },
                None,
            ),
        ]

        edges = [
            # Architectural dependencies
            ("uks:arch:doric_order", "uses_material", "uks:mat:utx_package_architecture"),
            ("uks:arch:gothic_grammar", "implemented_via", "uks:ued:semisolid_brush"),
            ("uks:arch:pointed_arch", "sculpted_with", "uks:ued:2d_shape_editor"),
            ("uks:arch:curtain_wall", "anchors_to", "procedural:stepped_terrain_heightfield"),
            ("uks:arch:bastion_tower", "anchors_to", "procedural:stepped_terrain_heightfield"),
            ("uks:arch:gatehouse_barbican", "pathfinds_via", "procedural:ai_reachability_lattice"),
            ("uks:arch:scifi_brutalism", "textures_with", "uks:mat:utx_package_architecture"),
            ("uks:arch:spatial_sightlines", "governs_pathing", "procedural:ai_reachability_lattice"),

            # 3D math & engine dependencies
            ("uks:3d:csg_bsp_math", "enforces_watertightness", "procedural:watertight_bsp_math"),
            ("uks:3d:collision_hull", "bounds_pathing", "procedural:ai_reachability_lattice"),
            ("uks:3d:matinee_cinematic", "animates_in", "uks:ued:skybox_parallax"),

            # Texture dependencies
            ("uks:mat:procedural_noise_shaders", "renders_with_flags", "uks:ued:poly_flags_catalog"),
            ("uks:mat:uv_unwrapping", "aligns_on", "uks:3d:csg_bsp_math"),

            # Advanced UnrealEd technique relationships
            ("uks:ued:semisolid_brush", "satisfies_rule", "procedural:pcg_csg_stack"),
            ("uks:ued:zone_portals", "optimizes_bsp", "procedural:pcg_csg_stack"),
            ("uks:ued:warp_zones", "connects_sectors", "uks:arch:spatial_sightlines"),
            ("uks:ued:skybox_parallax", "implements_rule", "procedural:celestial_skybox_parallax"),
            ("uks:ued:2d_shape_editor", "generates_geometry_for", "uks:arch:gothic_grammar"),
        ]

        for concept_id, category, label, attrs, parents in concepts:
            self.uks_register_concept(
                concept_id=concept_id,
                category=category,
                label=label,
                attributes=attrs,
                parents=parents,
            )

        for src, rel, tgt in edges:
            self.uks_link_concepts(src, rel, tgt)

        logger.info(
            f"Universal Knowledge System (UKS) seeded successfully with {len(concepts)} master concepts and {len(edges)} ontology links."
        )





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
