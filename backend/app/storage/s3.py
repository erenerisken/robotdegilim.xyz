"""Mock S3 adapter with run/admin lock coordination."""

from __future__ import annotations

import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from app.core.constants import S3_ADMIN_LOCK_FILE, S3_ADMIN_OP_LOCK_FILE, S3_LOCK_FILE, S3_MOCK_DIR_NAME
from app.core.errors import AppError
from app.core.settings import get_settings
from app.storage.local import read_json as read_local_json, write_json as write_local_json

_run_lock_held = False


def _mock_dir() -> Path:
    """Return local directory that emulates S3 storage."""
    base = Path(__file__).resolve().parents[2] / S3_MOCK_DIR_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def _resolve_key_path(key: str) -> Path:
    """Resolve and validate S3 key path under mock storage root."""
    key_path = Path(key)
    if key_path.is_absolute() or ".." in key_path.parts:
        raise AppError("Invalid key path.", "S3_INVALID_KEY", context={"key": key})
    return _mock_dir() / key_path


def _lock_path(*, admin: bool = False, admin_op: bool = False) -> Path:
    """Return lock file path under mock S3 directory."""
    if admin_op:
        return _mock_dir() / S3_ADMIN_OP_LOCK_FILE
    return _mock_dir() / (S3_ADMIN_LOCK_FILE if admin else S3_LOCK_FILE)


def _read_json_payload(path: Path) -> dict[str, Any] | None:
    """Read JSON payload from file and normalize invalid payloads as None."""
    if not path.exists():
        return None
    try:
        payload = read_local_json(path)
        if not isinstance(payload, dict) or len(payload) == 0:
            return None
        return payload
    except Exception:
        return None


def _write_json_payload(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON payload atomically (best effort) to avoid partial lock files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    write_local_json(tmp_path, payload)
    tmp_path.replace(path)


def _is_expired(payload: dict[str, Any] | None, *, now: float | None = None) -> bool:
    """Return True when payload is missing or its expires_at is in the past."""
    if not payload:
        return True
    current = time.time() if now is None else now
    try:
        return float(payload.get("expires_at", 0.0)) <= current
    except Exception:
        return True


def _active_admin_lock_data() -> dict[str, Any] | None:
    """Return active admin lock payload and cleanup stale lock file."""
    path = _lock_path(admin=True)
    payload = _read_json_payload(path)
    if _is_expired(payload):
        path.unlink(missing_ok=True)
        return None
    return payload


def _active_admin_op_lock_data() -> dict[str, Any] | None:
    """Return active admin op-lock payload if it matches active admin lock token."""
    op_path = _lock_path(admin_op=True)
    op_payload = _read_json_payload(op_path)
    if _is_expired(op_payload):
        op_path.unlink(missing_ok=True)
        return None

    admin_payload = _active_admin_lock_data()
    if not admin_payload:
        op_path.unlink(missing_ok=True)
        return None

    if op_payload.get("holder_token") != admin_payload.get("token"):
        op_path.unlink(missing_ok=True)
        return None
    return op_payload


def _ensure_run_mutation_allowed(operation: str, **context: Any) -> None:
    """Raise when run-side S3 mutation is not currently allowed."""
    if not _run_lock_held:
        raise AppError(f"Run lock not acquired before {operation}.", "LOCK_NOT_ACQUIRED", context=context)
    if admin_lock_exists():
        raise AppError(
            "Run-side mutation blocked because admin lock is active.",
            "OPERATION_BLOCKED_ADMIN_LOCK",
            context=context,
        )


def _ensure_admin_mutation_allowed(operation: str, **context: Any) -> None:
    """Raise when admin-side S3 mutation is not currently allowed."""
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


def acquire_lock() -> bool:
    """Acquire run lock for this instance if available and admin lock is not active."""
    global _run_lock_held
    try:
        if admin_lock_exists():
            return False
        if _run_lock_held:
            return True

        lock_path = _lock_path()
        now = time.time()
        settings = get_settings()
        current_payload = _read_json_payload(lock_path)
        if current_payload and not _is_expired(current_payload, now=now):
            return False

        payload = {
            "owner": settings.S3_LOCK_OWNER_ID,
            "acquired_at": now,
            "expires_at": now + float(settings.S3_LOCK_TIMEOUT_SECONDS),
        }
        _write_json_payload(lock_path, payload)
        _run_lock_held = True
        return True
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError("Failed to acquire run lock.", "LOCK_ACQUIRE_FAILED", cause=e)


def release_lock() -> bool:
    """Release run lock when current lock owner matches this instance."""
    global _run_lock_held
    try:
        if not _run_lock_held:
            return True

        lock_path = _lock_path()
        payload = _read_json_payload(lock_path)
        owner_id = get_settings().S3_LOCK_OWNER_ID

        if not payload:
            _run_lock_held = False
            return False

        if payload.get("owner") != owner_id:
            _run_lock_held = False
            return False

        lock_path.unlink(missing_ok=True)
        _run_lock_held = False
        return True
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError("Failed to release run lock.", "LOCK_RELEASE_FAILED", cause=e)


def upload_file(local_path: str | Path, key: str, _admin: bool = False) -> str:
    """Upload a local file to mock S3 key path (mutating; lock-guarded)."""
    try:
        _ensure_mutation_allowed(admin=_admin, operation="upload_file", local_path=str(local_path), key=key)
        src = Path(local_path)
        if not src.exists():
            raise AppError(
                "Upload source path does not exist.",
                "UPLOAD_FILE_FAILED",
                context={"local_path": str(local_path), "key": key},
            )
        dst = _resolve_key_path(key)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return str(dst)
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to upload file to S3 mock.",
            "UPLOAD_FILE_FAILED",
            context={"local_path": str(local_path), "key": key},
            cause=e,
        )


def download_file(key: str, local_path: str | Path) -> str:
    """Download a mock S3 key to local path (read-only; allowed during admin preemption)."""
    try:
        src = _resolve_key_path(key)
        if not src.exists():
            raise AppError(
                "S3 key does not exist.",
                "DOWNLOAD_FILE_FAILED",
                context={"key": key, "local_path": str(local_path)},
            )
        dst = Path(local_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return str(dst)
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to download file from S3 mock.",
            "DOWNLOAD_FILE_FAILED",
            context={"key": key, "local_path": str(local_path)},
            cause=e,
        )


def s3_file_exists(key: str) -> bool:
    """Check whether key exists in mock S3 (read-only)."""
    try:
        return _resolve_key_path(key).exists()
    except AppError:
        return False


def delete_file(key: str, _admin: bool = False) -> bool:
    """Delete key from mock S3 (mutating; lock-guarded)."""
    try:
        _ensure_mutation_allowed(admin=_admin, operation="delete_file", key=key)
        path = _resolve_key_path(key)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to delete file from S3 mock.",
            "DELETE_FILE_FAILED",
            context={"key": key},
            cause=e,
        )


def admin_lock_exists() -> bool:
    """Return whether admin lock is currently active."""
    return _active_admin_lock_data() is not None


def admin_op_lock_exists() -> bool:
    """Return whether admin operation lock is currently active and valid."""
    return _active_admin_op_lock_data() is not None


def admin_acquire_lock() -> dict[str, Any]:
    """Acquire admin lock and return acquisition status with lock metadata."""
    try:
        now = time.time()
        path = _lock_path(admin=True)
        current_payload = _read_json_payload(path)
        if current_payload and not _is_expired(current_payload, now=now):
            return {"acquired": False, "status": admin_lock_status()}

        token = str(uuid.uuid4())
        settings = get_settings()
        payload = {
            "owner": settings.S3_LOCK_OWNER_ID,
            "token": token,
            "acquired_at": now,
            "expires_at": now + float(settings.ADMIN_LOCK_TIMEOUT_SECONDS),
        }
        _write_json_payload(path, payload)
        return {"acquired": True, "token": token, "status": admin_lock_status()}
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to acquire admin lock.",
            "ADMIN_LOCK_ACQUIRE_FAILED",
            cause=e,
        )


def admin_validate_lock_token(token: str | None) -> bool:
    """Return True when token matches active admin lock token."""
    if not token:
        return False
    lock_payload = _active_admin_lock_data()
    if not lock_payload:
        return False
    return lock_payload.get("token") == token


def admin_release_lock(token: str | None) -> bool:
    """Release admin lock when token is valid and no admin operation is running."""
    try:
        if not admin_validate_lock_token(token):
            return False
        if admin_op_lock_exists():
            return False

        _lock_path(admin=True).unlink(missing_ok=True)
        _lock_path(admin_op=True).unlink(missing_ok=True)
        return True
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to release admin lock.",
            "ADMIN_LOCK_RELEASE_FAILED",
            cause=e,
        )


def admin_lock_status() -> dict[str, Any]:
    """Return admin lock status metadata without exposing lock token."""
    lock_payload = _active_admin_lock_data()
    if not lock_payload:
        return {"active": False}
    return {
        "active": True,
        "owner": lock_payload.get("owner"),
        "acquired_at": lock_payload.get("acquired_at"),
        "expires_at": lock_payload.get("expires_at"),
    }


def admin_acquire_op_lock(token: str | None) -> bool:
    """Acquire admin operation lock for validated admin token."""
    if not admin_validate_lock_token(token):
        return False
    if admin_op_lock_exists():
        return False

    now = time.time()
    expires_in = float(get_settings().ADMIN_LOCK_TIMEOUT_SECONDS)
    payload = {
        "holder_token": token,
        "acquired_at": now,
        "expires_at": now + expires_in,
    }
    _write_json_payload(_lock_path(admin_op=True), payload)
    return True


def admin_release_op_lock(token: str | None) -> bool:
    """Release admin operation lock when holder token matches."""
    path = _lock_path(admin_op=True)
    payload = _read_json_payload(path)
    if not payload:
        return True
    if payload.get("holder_token") != token:
        return False
    path.unlink(missing_ok=True)
    return True
