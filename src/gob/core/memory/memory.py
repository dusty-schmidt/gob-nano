import sqlite3
import json
import pickle
from pathlib import Path
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages persistent memory storage with SQLite and FAISS vector search support"""
    
    def __init__(self, db_path: str = "memory.db"):
        """Initialize memory manager with SQLite database and optional FAISS vector index"""
        # Determine absolute path relative to this file
        base_dir = Path(__file__).parent
        self.db_path = base_dir / db_path
        
        # FAISS index is in .a0proj/memory/ inside project root
        # base_dir is src/gob/core/memory, so parent.parent.parent.parent = project root
        project_root = base_dir.parent.parent.parent.parent
        self.faiss_index_path = project_root / ".a0proj" / "memory" / "index.faiss"
        self.faiss_meta_path = project_root / ".a0proj" / "memory" / "index.pkl"
        self._index: Optional['faiss.IndexFlatL2'] = None
        self._metadata: List[Dict] = []
        
        self._init_db()
        self._load_faiss_index()
    
    def _load_faiss_index(self):
        """Load FAISS vector index for semantic memory retrieval"""
        try:
            import faiss
            if self._index is None and self.faiss_index_path.exists():
                try:
                    self._index = faiss.read_index(str(self.faiss_index_path))
                    with open(self.faiss_meta_path, "rb") as f:
                        raw_meta = pickle.load(f)
                    
                    # Extract text content from LangChain InMemoryDocstore tuple format
                    # raw_meta is a tuple: (InMemoryDocstore, dict)
                    # The docstore contains Document objects with page_content
                    self._metadata = []
                    
                    if isinstance(raw_meta, tuple) and len(raw_meta) >= 1:
                        docstore = raw_meta[0]
                        # docstore is an InMemoryDocstore object
                        # It has a _dict attribute containing Document objects
                        if hasattr(docstore, '_dict'):
                            for doc in docstore._dict.values():
                                if hasattr(doc, 'page_content'):
                                    # Document.page_content contains the actual memory text
                                    self._metadata.append({
                                        "id": doc.metadata.get('id', -1),
                                        "text": doc.page_content,
                                        "area": doc.metadata.get('area', "main")
                                    })
                                elif isinstance(doc, str):
                                    # Fallback if doc is raw string
                                    self._metadata.append({
                                        "id": -1,
                                        "text": doc,
                                        "area": "main"
                                    })
                    
                    # Also create metadata index for backward compatibility
                    if len(self._metadata) < self._index.ntotal:
                        logger.warning(f"Extracted {len(self._metadata)} memories from docstore, but index has {self._index.ntotal} vectors")
                        logger.info("Vector search will use extracted memories where available")
                    
                    logger.info(f"Loaded FAISS index with {self._index.ntotal} vectors and extracted {len(self._metadata)} text memories")
                    
                except Exception as e:
                    logger.error(f"Could not load FAISS index metadata: {e}")
                    logger.error(f"Metadata will not be available for recall - vector search disabled")
                    self._metadata = []
                    self._index = None
        except ImportError:
            logger.warning("faiss package not installed - vector search unavailable")
    def vector_search(self, query: str, k: int = 5, area: str = "main") -> List[Dict]:
        """Search vector index and return relevant memories by similarity"""
        try:
            import numpy as np
            if self._index is None:
                logger.warning("Vector index not loaded - semantic search unavailable")
                return []
            
            # Encode query using same embedding model as training
            from src.gob.core.llm_client import EmbeddingClient
            embed_client = EmbeddingClient()
            query_vec = embed_client.embed(query).reshape(1, -1)
            
            # Search
            distances, indices = self._index.search(query_vec, k)
            
            # Return results with text content
            results = []
            for i, dist in zip(indices[0], distances[0]):
                if i < len(self._metadata):
                    # self._metadata now contains proper dicts with text field
                    meta = self._metadata[i]
                    results.append({
                        "id": meta.get("id", i),
                        "text": meta.get("text", ""),
                        "score": float(dist),
                        "area": meta.get("area", area)
                    })
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def get_vector_based_memories(self, query: str, limit: int = 8, area: str = "main") -> List[Dict]:
        """Get relevant memories using vector similarity search (convenience wrapper)"""
        return self.vector_search(query, k=limit, area=area)
    
    def _init_db(self):
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversations table for chat logs
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
            
            # Knowledge table for summarized memory/key-value
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    tags TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Settings table for agent state
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
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
    
    def get_conversations(self, session_id: str, limit: int = 10):
        """Retrieve recent conversation history for a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            # Reverse to get chronological order
            return [dict(row) for row in reversed(rows)]
    
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
    
    def get_knowledge(self, key: str):
        """Retrieve a knowledge entry by key."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM knowledge WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_all_knowledge(self):
        """Retrieve all knowledge entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT key, value, tags FROM knowledge")
            return [dict(row) for row in cursor.fetchall()]
    
    def add_memory_for_vector_search(self, text: str, area: str = "main") -> str:
        """Register memory for vector search (called by orchestrator after tool execution)"""
        pass  # Future: embed and add to FAISS index
