import sqlite3
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, db_path: str = "memory.db"):
        # Determine absolute path relative to this file
        base_dir = Path(__file__).parent
        self.db_path = base_dir / db_path
        self._init_db()

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
