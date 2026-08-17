"""Cryptographic Approval Manager for High/Medium Risk Tool Confirmations."""

import hashlib
import hmac
import json
import os
import time
from typing import Any

from jarvis.config.settings import get_settings
from jarvis.core.contracts import TaskStep


def canonicalize_args(args: dict[str, Any] | None) -> str:
    """Deterministically serialize tool arguments for HMAC binding."""
    if not args:
        return "{}"
    return json.dumps(args, sort_keys=True, separators=(",", ":"))


def generate_approval_token(
    task_id: str,
    step_id: str,
    tool_id: str,
    risk_level: str,
    tool_input: dict[str, Any] | None = None,
    secret_key: str | None = None,
    expires_at: int | None = None,
    nonce: str | None = None,
) -> str:
    """Generate a HMAC-SHA256 token bound to task ID, step ID, exact arguments, expiry timestamp, and nonce."""
    if not secret_key:
        secret_key = get_settings().approval_secret_key
    if not secret_key:
        raise ValueError("Approval secret key is not configured in settings or credentials.")
    if expires_at is None:
        expires_at = int(time.time()) + 600  # Default 10 min TTL
    if nonce is None:
        nonce = os.urandom(8).hex()

    key_bytes = secret_key.encode("utf-8")
    canonical_args = canonicalize_args(tool_input)
    msg = f"{task_id}:{step_id}:{tool_id}:{risk_level}:{canonical_args}:{expires_at}:{nonce}".encode("utf-8")
    signature = hmac.new(key_bytes, msg, hashlib.sha256).hexdigest()
    return f"{expires_at}:{nonce}:{signature}"


def verify_approval(
    task_id: str,
    step: TaskStep,
    approval_token: str | None,
    secret_key: str | None = None,
) -> bool:
    """Verify that approval token is un-expired, un-tampered, and bound to exact task parameters."""
    if not approval_token:
        return False

    parts = approval_token.split(":")
    if len(parts) == 3:
        try:
            expires_at = int(parts[0])
            nonce = parts[1]
        except ValueError:
            return False

        if expires_at < int(time.time()):
            return False

        risk_str = step.risk_level.value if hasattr(step.risk_level, "value") else str(step.risk_level)
        expected = generate_approval_token(
            task_id=task_id,
            step_id=step.step_id,
            tool_id=step.tool_id,
            risk_level=risk_str,
            tool_input=step.tool_input,
            secret_key=secret_key,
            expires_at=expires_at,
            nonce=nonce,
        )
        return hmac.compare_digest(expected, approval_token)

    # Legacy fallback verification for simple HMAC hex strings
    risk_str = step.risk_level.value if hasattr(step.risk_level, "value") else str(step.risk_level)
    if secret_key is None:
        secret_key = get_settings().approval_secret_key
    key_bytes = secret_key.encode("utf-8")
    canonical_args = canonicalize_args(step.tool_input)
    legacy_msg = f"{task_id}:{step.step_id}:{step.tool_id}:{risk_str}:{canonical_args}".encode("utf-8")
    legacy_expected = hmac.new(key_bytes, legacy_msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(legacy_expected, approval_token)

