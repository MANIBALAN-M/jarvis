"""Cryptographic Approval Manager for High/Medium Risk Tool Confirmations."""

import hashlib
import hmac

from jarvis.core.contracts import TaskStep

SECRET_KEY = b"jarvis_local_security_secret_key_v1"


def generate_approval_token(task_id: str, step_id: str, tool_id: str) -> str:
    """Generate a HMAC-SHA256 token proving explicit user confirmation."""
    msg = f"{task_id}:{step_id}:{tool_id}".encode()
    return hmac.new(SECRET_KEY, msg, hashlib.sha256).hexdigest()


def verify_approval(task_id: str, step: TaskStep, approval_token: str | None) -> bool:
    """Verify that approval token is valid for the target step."""
    if not approval_token:
        return False
    expected = generate_approval_token(task_id, step.step_id, step.tool_id)
    return hmac.compare_digest(expected, approval_token)
