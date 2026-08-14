"""
SQLite Audit Repository for persistent audit logging.
"""

import time
from typing import Any
from uuid import uuid4

from jarvis.storage.sqlite import SQLiteManager


class SQLiteAuditRepository:
    """Repository handling immutable append-only audit records in SQLite."""

    def __init__(self, manager: SQLiteManager):
        self.manager = manager

    def record_event(
        self,
        event_type: str,
        tool_id: str,
        risk_level: str,
        decision: str,
        args_summary: str = "",
        result_status: str = "",
        details: str = "",
    ) -> str:
        """Insert structured audit event log entry."""
        event_id = str(uuid4())
        now = time.time()
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_events (
                    event_id, timestamp, event_type, tool_id, risk_level,
                    decision, args_summary, result_status, details
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    now,
                    event_type,
                    tool_id,
                    risk_level,
                    decision,
                    args_summary,
                    result_status,
                    details,
                ),
            )
            conn.commit()
        return event_id

    def query_events(self, limit: int = 50) -> list[dict[str, Any]]:
        """Query recent audit events."""
        with self.manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
