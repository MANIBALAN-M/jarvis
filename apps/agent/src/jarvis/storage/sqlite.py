"""
SQLite Local Persistence Engine for JARVIS Local Agent.
"""

import sqlite3


class SQLiteManager:
    """Manages SQLite connection and DDL schema initialization."""

    def __init__(self, db_path: str = "jarvis_local.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Create initial database tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    command_id TEXT NOT NULL,
                    goal_summary TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)

            # Task Steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_steps (
                    step_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    tool_id TEXT NOT NULL,
                    tool_input TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    requires_approval INTEGER NOT NULL,
                    description TEXT,
                    output_summary TEXT,
                    error_message TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
                )
            """)

            # Audit Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    tool_id TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    args_summary TEXT,
                    result_status TEXT,
                    details TEXT
                )
            """)
            conn.commit()


_db_instance: SQLiteManager | None = None


def get_sqlite_manager(db_path: str = "jarvis_local.db") -> SQLiteManager:
    global _db_instance
    if _db_instance is None or _db_instance.db_path != db_path:
        _db_instance = SQLiteManager(db_path)
    return _db_instance
