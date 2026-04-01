"""
Memory Manager for GOB
SQLite-based conversation and knowledge storage.
Vector search (FAISS) is lazy-loaded only when explicitly called.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent memory with SQLite. Vector search is optional and lazy."""

    def __init__(self, db_path: str = None):
        """Initialize with SQLite only. No heavy imports."""
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Default: memory.db next to this file
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

            conn.commit()

    # ── Conversation Storage ─────────────────────────────────────────────

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
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]

    # ── Knowledge Storage ────────────────────────────────────────────────

    def add_knowledge(self, key: str, value: str, tags: str = ""):
        """Add or update a knowledge entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO knowledge (key, value, tags) VALUES (?, ?, ?)",
                    (key, value, tags)
                )
                conn.commit()
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

    # ── Vector Search (lazy, optional) ───────────────────────────────────

    def _ensure_faiss(self):
        """Lazy-load FAISS index. Only called when vector search is requested."""
        if self._faiss_loaded:
            return

        self._faiss_loaded = True  # Mark as attempted even if it fails

        try:
            import faiss
            import pickle

            project_root = Path(__file__).parent.parent.parent.parent
            index_path = project_root / ".a0proj" / "memory" / "index.faiss"
            meta_path = project_root / ".a0proj" / "memory" / "index.pkl"

            if not index_path.exists():
                logger.debug("No FAISS index found, vector search unavailable")
                return

            self._index = faiss.read_index(str(index_path))

            with open(meta_path, "rb") as f:
                raw_meta = pickle.load(f)

            # Extract text from LangChain docstore format
            self._metadata = []
            if isinstance(raw_meta, tuple) and len(raw_meta) >= 1:
                docstore = raw_meta[0]
                if hasattr(docstore, '_dict'):
                    for doc in docstore._dict.values():
                        if hasattr(doc, 'page_content'):
                            self._metadata.append({
                                "text": doc.page_content,
                                "area": doc.metadata.get('area', 'main')
                            })

            logger.info(f"FAISS loaded: {self._index.ntotal} vectors, {len(self._metadata)} docs")

        except ImportError:
            logger.debug("faiss not installed, vector search unavailable")
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}")
            self._index = None

    def get_vector_based_memories(self, query: str, limit: int = 5, area: str = "main") -> List[Dict]:
        """Search for relevant memories using vector similarity. Lazy-loads FAISS."""
        self._ensure_faiss()

        if self._index is None:
            return []

        try:
            import numpy as np
            from gob.core.llm_client import EmbeddingClient

            embed_client = EmbeddingClient()
            query_vec = embed_client.embed(query).reshape(1, -1)

            distances, indices = self._index.search(query_vec, limit)

            results = []
            for i, dist in zip(indices[0], distances[0]):
                if 0 <= i < len(self._metadata):
                    meta = self._metadata[i]
                    results.append({
                        "text": meta.get("text", ""),
                        "score": float(dist),
                        "area": meta.get("area", area)
                    })
            return results

        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            return []
