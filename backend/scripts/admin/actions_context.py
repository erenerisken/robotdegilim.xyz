"""Admin context actions."""

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


def context_get() -> tuple[int, dict[str, Any]]:
    """Fetch current context snapshot."""
    return admin_post("context_get")


def context_clear_queue() -> tuple[int, dict[str, Any]]:
    """Clear context queue (mutating)."""
    return admin_post("context_clear_queue", lock_token=_require_token())


def context_reset_failures() -> tuple[int, dict[str, Any]]:
    """Reset context failure counter (mutating)."""
    return admin_post("context_reset_failures", lock_token=_require_token())


def context_unsuspend() -> tuple[int, dict[str, Any]]:
    """Unsuspend processing flag in context (mutating)."""
    return admin_post("context_unsuspend", lock_token=_require_token())
