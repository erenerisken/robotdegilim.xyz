"""Status publishing service for frontend busy/idle checks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from app.core.constants import STATUS_FILE
from app.storage.s3 import admin_lock_exists, run_lock_exists
from app.storage.s3.store import write_json_payload


StatusValue = Literal["idle", "busy"]


def _utc_now_iso() -> str:
    """Return UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def publish_status(status: StatusValue) -> None:
    """Publish status payload to public `status.json`."""
    write_json_payload(
        STATUS_FILE,
        {
            "status": status,
            "updated_at": _utc_now_iso(),
        },
        public_read=True,
    )


def compute_status_from_locks() -> StatusValue:
    """Compute status from shared run/admin lock truth."""
    if run_lock_exists() or admin_lock_exists():
        return "busy"
    return "idle"


def sync_status_from_locks() -> None:
    """Publish status derived from current lock state."""
    publish_status(compute_status_from_locks())

