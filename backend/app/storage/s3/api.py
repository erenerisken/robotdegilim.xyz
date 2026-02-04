"""Public object APIs with run/admin mutation guards."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.errors import AppError

from .common import _is_real_s3_enabled, _normalize_key, _mock_path
from .locks import admin_lock_exists, admin_op_lock_exists
from .state import is_run_lock_held
from .store import delete_object, object_exists, read_object_bytes, write_object_bytes


def _ensure_run_mutation_allowed(operation: str, **context: Any) -> None:
    """Raise when run-side storage mutation is not currently allowed."""
    if not is_run_lock_held():
        raise AppError(f"Run lock not acquired before {operation}.", "LOCK_NOT_ACQUIRED", context=context)
    if admin_lock_exists():
        raise AppError(
            "Run-side mutation blocked because admin lock is active.",
            "OPERATION_BLOCKED_ADMIN_LOCK",
            context=context,
        )


def _ensure_admin_mutation_allowed(operation: str, **context: Any) -> None:
    """Raise when admin-side storage mutation is not currently allowed."""
    if not admin_lock_exists():
        raise AppError(
            f"Admin lock not acquired before {operation}.",
            "ADMIN_LOCK_NOT_ACQUIRED",
            context=context,
        )
    if not admin_op_lock_exists():
        raise AppError(
            f"Admin operation lock not acquired before {operation}.",
            "ADMIN_OP_LOCK_NOT_ACQUIRED",
            context=context,
        )


def _ensure_mutation_allowed(*, admin: bool, operation: str, **context: Any) -> None:
    """Validate lock guards for mutating operations."""
    if admin:
        _ensure_admin_mutation_allowed(operation, **context)
    else:
        _ensure_run_mutation_allowed(operation, **context)


def upload_file(local_path: str | Path, key: str, _admin: bool = False) -> str:
    """Upload a local file to storage key path (mutating; lock-guarded)."""
    try:
        _ensure_mutation_allowed(admin=_admin, operation="upload_file", local_path=str(local_path), key=key)
        src = Path(local_path)
        if not src.exists():
            raise AppError(
                "Upload source path does not exist.",
                "UPLOAD_FILE_FAILED",
                context={"local_path": str(local_path), "key": key},
            )
        write_object_bytes(key, src.read_bytes())
        if _is_real_s3_enabled():
            return _normalize_key(key)
        return str(_mock_path(key))
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to upload file to storage.",
            "UPLOAD_FILE_FAILED",
            context={"local_path": str(local_path), "key": key},
            cause=e,
        )


def download_file(key: str, local_path: str | Path) -> str:
    """Download storage key to local path (read-only; allowed during admin preemption)."""
    try:
        content = read_object_bytes(key)
        if content is None:
            raise AppError(
                "Storage key does not exist.",
                "DOWNLOAD_FILE_FAILED",
                context={"key": key, "local_path": str(local_path)},
            )
        dst = Path(local_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(content)
        return str(dst)
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to download file from storage.",
            "DOWNLOAD_FILE_FAILED",
            context={"key": key, "local_path": str(local_path)},
            cause=e,
        )


def s3_file_exists(key: str) -> bool:
    """Check whether key exists in storage backend (read-only)."""
    try:
        return object_exists(key)
    except AppError:
        return False


def delete_file(key: str, _admin: bool = False) -> bool:
    """Delete key from storage backend (mutating; lock-guarded)."""
    try:
        _ensure_mutation_allowed(admin=_admin, operation="delete_file", key=key)
        return delete_object(key)
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to delete file from storage.",
            "DELETE_FILE_FAILED",
            context={"key": key},
            cause=e,
        )
