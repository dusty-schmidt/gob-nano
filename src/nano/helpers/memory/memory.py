"""Simple JSON-lines memory manager for NANO"""
import json
from pathlib import Path

class MemoryManager:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        # Ensure the parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def add_entry(self, entry: dict):
        """Append a JSON entry as a new line"""
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_all(self):
        """Read all entries from the JSONL file"""
        if not self.file_path.exists():
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def query(self, key, value):
        """Return entries where entry[key] == value"""
        return [e for e in self.get_all() if e.get(key) == value]
