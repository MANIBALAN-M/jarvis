"""Audit Logger bridging Policy/Tool actions to SQLite Audit Repository."""

from typing import Any

from jarvis.storage.repositories.audit_repository import SQLiteAuditRepository
from jarvis.storage.sqlite import get_sqlite_manager

SENSITIVE_KEYS = {"content", "password", "token", "secret", "key", "credentials"}


def sanitize_args_summary(args: dict[str, Any] | None) -> str:
    """Mask sensitive parameter values and summarize args for audit data minimization."""
    if not args:
        return ""
    sanitized: dict[str, Any] = {}
    for k, v in args.items():
        if k.lower() in SENSITIVE_KEYS:
            sanitized[k] = "[REDACTED]"
        else:
            val_str = str(v)
            sanitized[k] = val_str[:32] + "..." if len(val_str) > 32 else v

    res = str(sanitized)
    return res[:128]


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
        summary = sanitize_args_summary(args)
        return self.repo.record_event(
            event_type=event_type,
            tool_id=tool_id,
            risk_level=risk_level,
            decision=decision,
            args_summary=summary,
            result_status=result_status,
            details=details[:256],
        )
