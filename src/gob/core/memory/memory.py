"""Memory Manager for GOB with failure context tracking."""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent memory with SQLite and failure context storage."""

    def __init__(self, db_path: str = None):
        """Initialize with SQLite and create all tables.

        Args:
            db_path: Optional path to SQLite database file.
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(__file__).parent / "memory.db"

        self._faiss_loaded = False
        self._index = None
        self._metadata: List[Dict] = []
        self._init_db()
        logger.info(f"Memory initialized: {self.db_path}")

    def _init_db(self):
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    tags TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # New: Failure context table (Epic 3, Story 27)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS failure_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    exit_code INTEGER,
                    stdout TEXT,
                    stderr TEXT,
                    autopsy_report TEXT,
                    tool_name TEXT,
                    session_id TEXT DEFAULT 'default'
                )
            ''')
            conn.commit()

    def add_conversation(self, session_id: str, role: str, content: str, metadata: dict = None):
        """Add a message to the conversation log."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                meta_str = json.dumps(metadata) if metadata else None
                cursor.execute(
                    "INSERT INTO conversations (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                    (session_id, role, content, meta_str)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add conversation: {e}")

    def get_conversations(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve recent conversation history for a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
            return [dict(row) for row in reversed(cursor.fetchall())]

    def add_knowledge(self, key: str, value: str, tags: str = ""):
        """Add or update a knowledge entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO knowledge (key, value, tags) VALUES (?, ?, ?)",
                    (key, value, tags)
                )
        except Exception as e:
            logger.error(f"Failed to add knowledge: {e}")

    def get_knowledge(self, key: str) -> Optional[str]:
        """Retrieve a knowledge entry by key."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM knowledge WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_all_knowledge(self) -> List[Dict]:
        """Retrieve all knowledge entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT key, value, tags FROM knowledge")
            return [dict(row) for row in cursor.fetchall()]

    # ── Failure Context (Epic 3, Story 27) ───────────────────────────────

    def add_failure_log(
        self,
        exit_code: int,
        stdout: str,
        stderr: str,
        autopsy_report: str = "",
        tool_name: str = "",
        session_id: str = "default"
    ) -> None:
        """Store a failure record in SQLite.

        Args:
            exit_code: Container process exit code.
            stdout: Captured stdout output.
            stderr: Captured stderr output.
            autopsy_report: Structured failure analysis (optional).
            tool_name: Name of the failing tool (optional).
            session_id: Conversation session identifier.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO failure_context
                       (exit_code, stdout, stderr, autopsy_report, tool_name, session_id)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (exit_code, stdout, stderr, autopsy_report, tool_name, session_id)
                )
            logger.debug(f"Failure recorded: exit_code={exit_code}, tool={tool_name}")
        except Exception as e:
            logger.error(f"Failed to record failure: {e}")

    def get_recent_failures(self, limit: int = 5, session_id: str = "default") -> List[Dict[str, Any]]:
        """Return the N most recent failure records.

        Args:
            limit: Maximum number of records to return (default 5).
            session_id: Filter by session (default 'default').

        Returns:
            List of dictionaries with keys: id, timestamp, exit_code, stdout, stderr,
              autopsy_report, tool_name, session_id.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM failure_context WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to retrieve failures: {e}")
            return []

    # ── Vector Search (lazy, optional) ───────────────────────────────────

    def _ensure_faiss(self):
        """Lazy-load FAISS index. Only called when vector search is requested."""
        if self._faiss_loaded:
            return
        self._faiss_loaded = True
        try:
            import faiss, pickle
            project_root = Path(__file__).parent.parent.parent.parent
            index_path = project_root / ".a0proj" / "memory" / "index.faiss"
            meta_path = project_root / ".a0proj" / "memory" / "index.pkl"
            if not index_path.exists():
                return
            self._index = faiss.read_index(str(index_path))
            with open(meta_path, "rb") as f:
                raw_meta = pickle.load(f)
            self._metadata = []
            if isinstance(raw_meta, tuple) and len(raw_meta) >= 1:
                docstore = raw_meta[0]
                if hasattr(docstore, '_dict'):
                    for doc in docstore._dict.values():
                        if hasattr(doc, 'page_content'):
                            self._metadata.append({"text": doc.page_content, "area": doc.metadata.get('area', 'main')})
            logger.info(f"FAISS loaded: {self._index.ntotal} vectors")
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}")
            self._index = None

    def get_vector_based_memories(self, query: str, limit: int = 5, area: str = "main") -> List[Dict]:
        """Search for relevant memories using vector similarity."""
        self._ensure_faiss()
        if self._index is None:
            return []
        try:
            import numpy as np
            from gob.core.llm_client import EmbeddingClient
            query_vec = EmbeddingClient().embed(query).reshape(1, -1)
            distances, indices = self._index.search(query_vec, limit)
            return [{"text": self._metadata[i]["text"], "score": float(d), "area": self._metadata[i].get("area", area)} for i, d in zip(indices[0], distances[0]) if 0 <= i < len(self._metadata)]
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            return []
