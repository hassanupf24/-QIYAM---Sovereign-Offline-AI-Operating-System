import warnings
warnings.warn("SQLiteStore is deprecated. Please migrate to PostgresStore.", DeprecationWarning, stacklevel=2)

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger("memory.sqlite_store")

class SQLiteStore:
    def __init__(self):
        self.db_path = settings.SQLITE_DB_PATH
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_db()

    def _get_connection(self):
        # Enable WAL mode for better concurrency
        conn = sqlite3.connect(self.db_path, timeout=20.0)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _initialize_db(self):
        logger.info(f"Initializing SQLite database at {self.db_path}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            # Agent States table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, agent_name),
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            # Audit Log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    user_id TEXT,
                    details TEXT
                )
            """)
            conn.commit()

    def create_session(self, session_id: str, user_id: str, metadata: Dict[str, Any] = None) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sessions (session_id, user_id, metadata) VALUES (?, ?, ?)",
                (session_id, user_id, json.dumps(metadata or {}))
            )
            conn.commit()

    def add_message(self, session_id: str, role: str, content: str, tokens: int = 0) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, tokens) VALUES (?, ?, ?, ?)",
                (session_id, role, content, tokens)
            )
            # Update session timestamp
            cursor.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()

    def get_recent_messages(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            # Reverse to get chronological order
            return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in reversed(rows)]
            
    def log_audit_event(self, action: str, user_id: Optional[str] = None, details: Dict[str, Any] = None) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO audit_log (action, user_id, details) VALUES (?, ?, ?)",
                (action, user_id, json.dumps(details or {}))
            )
            conn.commit()
