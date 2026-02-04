"""Calling-based admin script runner.

Edit `main()` to call whichever scenario/action sequence you want.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from admin.actions import (  # type: ignore[import-not-found]
        context_clear_queue,
        context_get,
        context_reset_failures,
        context_unsuspend,
        lock_acquire,
        lock_release,
        lock_status,
        settings_get,
        settings_set,
    )
else:
    from .actions import (
        context_clear_queue,
        context_get,
        context_reset_failures,
        context_unsuspend,
        lock_acquire,
        lock_release,
        lock_status,
        settings_get,
        settings_set,
    )


def _print_response(name: str, result: tuple[int, dict[str, Any]]) -> None:
    """Pretty-print one action result."""
    status_code, body = result
    print(f"\n[{name}] HTTP {status_code}")
    print(f"status={body.get('status')} message={body.get('message')}")
    data = body.get("data")
    if data is not None:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def run_lock_flow() -> None:
    """Example lock acquire/status/release flow."""
    _print_response("lock_acquire", lock_acquire())
    _print_response("lock_status", lock_status())
    _print_response("lock_release", lock_release())


def run_context_recovery() -> None:
    """Example context recovery sequence under admin lock."""
    _print_response("lock_acquire", lock_acquire())
    _print_response("context_get", context_get())
    _print_response("context_clear_queue", context_clear_queue())
    _print_response("context_reset_failures", context_reset_failures())
    _print_response("context_unsuspend", context_unsuspend())
    _print_response("lock_release", lock_release())


def run_settings_patch() -> None:
    """Example settings read/update flow under admin lock."""
    _print_response("lock_acquire", lock_acquire())
    _print_response("settings_get", settings_get())
    _print_response(
        "settings_set",
        settings_set(
            {
                "HTTP_TIMEOUT": 20,
                "LOG_LEVEL": "INFO",
            }
        ),
    )
    _print_response("lock_release", lock_release())


def main() -> None:
    """Entry point for manual, calling-based admin operations."""
    # Choose one flow at a time by commenting/uncommenting:
    run_lock_flow()
    # run_context_recovery()
    # run_settings_patch()


if __name__ == "__main__":
    main()
