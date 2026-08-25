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
        sql = f"SELECT * FROM wisdom_insights {where_clause} ORDER BY confidence DESC, updated_at DESC LIMIT ?"
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
