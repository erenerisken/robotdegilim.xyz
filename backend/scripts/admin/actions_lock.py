"""Admin lock actions."""

from __future__ import annotations

from typing import Any

from .client import admin_post
from .token_store import clear_token, load_token, save_token


def lock_acquire() -> tuple[int, dict[str, Any]]:
    """Acquire admin lock and store token on success."""
    status_code, body = admin_post("admin_lock_acquire")
    token = body.get("data", {}).get("lock_token") if isinstance(body.get("data"), dict) else None
    if status_code == 200 and isinstance(token, str) and token:
        save_token(token)
    return status_code, body


def lock_status() -> tuple[int, dict[str, Any]]:
    """Fetch current admin lock status."""
    return admin_post("admin_lock_status")


def lock_release() -> tuple[int, dict[str, Any]]:
    """Release admin lock using saved token; clear token file on success."""
    token = load_token()
    if not token:
        raise RuntimeError("No lock token found. Acquire lock first or set backend/.admin_lock_token.")
    status_code, body = admin_post("admin_lock_release", lock_token=token)
    if status_code == 200:
        clear_token()
    return status_code, body
