"""Audit Logger bridging Policy/Tool actions to SQLite Audit Repository."""

from typing import Any

from jarvis.storage.repositories.audit_repository import SQLiteAuditRepository
from jarvis.storage.sqlite import get_sqlite_manager


class AuditLogger:
    """Central audit logging interface for security-relevant tool actions."""

    def __init__(self, repo: SQLiteAuditRepository | None = None):
        if repo is None:
            manager = get_sqlite_manager()
            repo = SQLiteAuditRepository(manager)
        self.repo = repo

    def log_action(
        self,
        event_type: str,
        tool_id: str,
        risk_level: str,
        decision: str,
        args: dict[str, Any] | None = None,
        result_status: str = "",
        details: str = "",
    ) -> str:
        args_str = str(args) if args else ""
        return self.repo.record_event(
            event_type=event_type,
            tool_id=tool_id,
            risk_level=risk_level,
            decision=decision,
            args_summary=args_str[:256],
            result_status=result_status,
            details=details,
        )
