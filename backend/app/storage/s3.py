"""Mock S3 storage adapter with local lock ownership enforcement."""

import json
import shutil
import time
from pathlib import Path
from typing import Any

from app.core.constants import S3_ADMIN_LOCK_FILE, S3_LOCK_FILE, S3_MOCK_DIR_NAME
from app.core.errors import AppError
from app.core.settings import get_settings

_lock_acquired = False

def _lock_path(_admin:bool=False) -> Path:
    """Return lock file path in mock S3 directory."""
    base = _mock_dir()
    return base / (S3_ADMIN_LOCK_FILE if _admin else S3_LOCK_FILE)

def _mock_dir() -> Path:
    """Return local directory that emulates S3 storage."""
    base = Path(__file__).resolve().parents[2] / S3_MOCK_DIR_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def _ensure_lock(operation: str, **context: Any) -> None:
    """Raise when lock is not currently held by this instance."""
    if not _lock_acquired:
        raise AppError(
            f"Lock not acquired before {operation}",
            "LOCK_NOT_ACQUIRED",
            context=context,
        )

def acquire_lock() -> bool:
    """Acquire lock for this instance if available or expired."""
    try:
        if admin_lock_exists():
            return False
        global _lock_acquired
        if not _lock_acquired:
            lock_file_path = _lock_path()
            current_time = time.time()
            settings = get_settings()
            timeout = float(settings.S3_LOCK_TIMEOUT_SECONDS)

            if not lock_file_path.exists():
                lock = {"owner": settings.S3_LOCK_OWNER_ID, "acquired_at": current_time, "expires_at": current_time + timeout}
                lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
                _lock_acquired = True
                return True

            lock_data: dict[str, Any] = json.loads(lock_file_path.read_text(encoding="utf-8"))

            if float(lock_data.get("expires_at", 0)) < current_time:
                lock = {"owner": settings.S3_LOCK_OWNER_ID, "acquired_at": current_time, "expires_at": current_time + timeout}
                lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
                _lock_acquired = True
                return True

            return False
        return True
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to acquire lock", "LOCK_ACQUIRE_FAILED", cause=e)
        raise err

def release_lock() -> bool:
    """Release lock if owned by this instance."""
    try:
        global _lock_acquired
        if _lock_acquired:
            lock_file_path = _lock_path()
            settings = get_settings()
            if not lock_file_path.exists():
                _lock_acquired = False
                return False
        
            lock_data = json.loads(lock_file_path.read_text(encoding="utf-8"))

            if lock_data.get("owner") == settings.S3_LOCK_OWNER_ID:
                lock_file_path.unlink(missing_ok=True)
                _lock_acquired = False
                return True
            _lock_acquired = False
            return False
        return True
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to release lock", "LOCK_RELEASE_FAILED", cause=e)
        raise err


def upload_file(local_path: str | Path, key: str, _admin: bool = False) -> str:
    """Upload local file to mock S3 key path."""
    try:
        _ensure_locks(_admin, "uploading file to s3", local_path=local_path, key=key)
        src = Path(local_path)
        if not src.exists():
            raise AppError("Failed to upload the file to s3", "UPLOAD_FILE_FAILED", context={"local_path": local_path, "key": key, "reason": "path does not exist"})
        dst = _mock_dir() / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return str(dst)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to upload the file to s3", "UPLOAD_FILE_FAILED", context={"local_path": local_path, "key": key}, cause=e)
        raise err


def download_file(key: str, local_path: str | Path) -> str:
    """Download mock S3 key to local path."""
    try:
        src = _mock_dir() / key
        if not src.exists():
            raise AppError("Failed to download the file from s3", "DOWNLOAD_FILE_FAILED", context={"local_path": local_path, "key": key, "reason": "key does not exist"})
        dst = Path(local_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return str(dst)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to download the file from s3", "DOWNLOAD_FILE_FAILED", context={"local_path": local_path, "key": key}, cause=e)
        raise err


def s3_file_exists(key: str) -> bool:
    """Check whether a key exists in mock S3."""
    return (_mock_dir() / key).exists()


def delete_file(key: str, _admin:bool=False) -> bool:
    """Delete a key from mock S3 if present."""
    _ensure_locks(_admin, "deleting file from s3", key=key)
    path = _mock_dir() / key
    if path.exists():
        path.unlink()
        return True
    return False

# Admin lock functions

_admin_lock_acquired = False

def _ensure_admin_lock(operation: str, **context: Any) -> None:
    """Raise when admin lock is not currently held by this instance."""
    if not _admin_lock_acquired:
        raise AppError(
            f"Admin lock not acquired before {operation}",
            "ADMIN_LOCK_NOT_ACQUIRED",
            context=context,
        )

def _ensure_no_admin_lock() -> None:
    if admin_lock_exists():
        raise AppError(
            "Operation blocked due to existing admin lock",
            "OPERATION_BLOCKED_ADMIN_LOCK",
        )
    
def _ensure_locks(_admin: bool, operation: str, **context: Any) -> None:
    """Raise when required lock conditions are not met."""
    if _admin:
        _ensure_admin_lock(operation, **context)
    else:
        _ensure_lock(operation, **context)
        _ensure_no_admin_lock()

def admin_acquire_lock() -> bool:
    """Acquire admin lock for this instance if available or expired."""
    try:
        global _admin_lock_acquired
        if not _admin_lock_acquired:
            lock_file_path = _lock_path(_admin=True)
            current_time = time.time()
            settings = get_settings()
            timeout = float(settings.ADMIN_LOCK_TIMEOUT_SECONDS)

            if not lock_file_path.exists():
                lock = {"owner": settings.S3_LOCK_OWNER_ID, "acquired_at": current_time, "expires_at": current_time + timeout}
                lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
                _admin_lock_acquired = True
                return True

            lock_data: dict[str, Any] = json.loads(lock_file_path.read_text(encoding="utf-8"))

            if float(lock_data.get("expires_at", 0)) < current_time:
                lock = {"owner": settings.S3_LOCK_OWNER_ID, "acquired_at": current_time, "expires_at": current_time + timeout}
                lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
                _admin_lock_acquired = True
                return True

            return False
        return True
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to acquire admin lock", "ADMIN_LOCK_ACQUIRE_FAILED", cause=e)
        raise err

def admin_release_lock() -> bool:
    """Release admin lock if owned by this instance."""
    try:
        global _admin_lock_acquired
        if _admin_lock_acquired:
            lock_file_path = _lock_path(_admin=True)
            settings = get_settings()
            if not lock_file_path.exists():
                _admin_lock_acquired = False
                return False
        
            lock_data = json.loads(lock_file_path.read_text(encoding="utf-8"))

            if lock_data.get("owner") == settings.S3_LOCK_OWNER_ID:
                lock_file_path.unlink(missing_ok=True)
                _admin_lock_acquired = False
                return True
            _admin_lock_acquired = False
            return False
        return True
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to release admin lock", "ADMIN_LOCK_RELEASE_FAILED", cause=e)
        raise err

def admin_lock_exists() -> bool:
    """Check if the admin lock is currently acquired by any instance."""
    return (_mock_dir() / S3_ADMIN_LOCK_FILE).exists()


def admin_lock_acquired() -> bool:
    """Check whether admin lock is held by this instance."""
    return _admin_lock_acquired


def admin_lock_status() -> dict[str, Any]:
    """Return admin lock status metadata."""
    lock_file = _lock_path(_admin=True)
    if not lock_file.exists():
        return {"active": False, "owned": _admin_lock_acquired}
    try:
        data: dict[str, Any] = json.loads(lock_file.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    return {
        "active": True,
        "owned": _admin_lock_acquired,
        "owner": data.get("owner"),
        "acquired_at": data.get("acquired_at"),
        "expires_at": data.get("expires_at"),
    }
