"""Internal mutable state for S3 storage adapter."""

from typing import Any

_run_lock_held = False
_s3_client: Any | None = None


def is_run_lock_held() -> bool:
    """Return whether the current process holds the run lock."""
    return _run_lock_held


def set_run_lock_held(value: bool) -> None:
    """Set in-memory run lock ownership flag."""
    global _run_lock_held
    _run_lock_held = value


def get_cached_client() -> Any | None:
    """Return cached boto3 client if initialized."""
    return _s3_client


def set_cached_client(client: Any | None) -> None:
    """Set cached boto3 client reference."""
    global _s3_client
    _s3_client = client
