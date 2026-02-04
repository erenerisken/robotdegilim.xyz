"""Admin settings actions."""

from __future__ import annotations

from typing import Any

from .client import admin_post
from .token_store import load_token


def _require_token() -> str:
    """Return lock token or raise clear error for mutating actions."""
    token = load_token()
    if not token:
        raise RuntimeError("No lock token found. Acquire lock first or set backend/.admin_lock_token.")
    return token


def settings_get() -> tuple[int, dict[str, Any]]:
    """Fetch masked public settings via admin API."""
    return admin_post("settings_get")


def settings_set(updates: dict[str, object]) -> tuple[int, dict[str, Any]]:
    """Apply settings updates (mutating)."""
    if not isinstance(updates, dict):
        raise RuntimeError("updates must be a dict.")
    payload = {"updates": updates}
    return admin_post("settings_set", payload=payload, lock_token=_require_token())
