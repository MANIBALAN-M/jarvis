"""Per-installation Secure Credential Storage & Generation."""

import json
import os
import secrets
from pathlib import Path

CREDENTIALS_DIR = Path.home() / ".jarvis"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"


def load_or_create_credentials() -> dict[str, str]:
    """Load or generate per-installation API auth token and approval secret key."""
    token = os.environ.get("JARVIS_API_AUTH_TOKEN")
    secret = os.environ.get("JARVIS_APPROVAL_SECRET_KEY")

    if token and secret:
        return {
            "api_auth_token": token,
            "approval_secret_key": secret,
        }

    file_creds: dict[str, str] = {}
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                file_creds = json.load(f)
        except (OSError, json.JSONDecodeError):
            file_creds = {}

    final_token = token or file_creds.get("api_auth_token") or secrets.token_hex(32)
    final_secret = secret or file_creds.get("approval_secret_key") or secrets.token_hex(32)

    if not CREDENTIALS_FILE.exists() or file_creds.get("api_auth_token") != final_token or file_creds.get("approval_secret_key") != final_secret:
        try:
            CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
            with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "api_auth_token": final_token,
                        "approval_secret_key": final_secret,
                    },
                    f,
                    indent=2,
                )
            if hasattr(os, "chmod"):
                os.chmod(CREDENTIALS_FILE, 0o600)
        except OSError:
            pass

    return {
        "api_auth_token": final_token,
        "approval_secret_key": final_secret,
    }
