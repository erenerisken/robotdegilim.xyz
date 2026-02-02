"""Mock S3 storage adapter with local lock ownership enforcement."""

import json
import shutil
import time
from pathlib import Path
from typing import Any

from app.core.errors import AppError
from app.core.settings import get_settings

_lock_acquired = False


def _lock_path() -> Path:
    """Return lock file path in mock S3 directory."""
    base = _mock_dir()
    return base / "lockfile.lock"


def _mock_dir() -> Path:
    """Return local directory that emulates S3 storage."""
    base = Path(__file__).resolve().parents[2] / "s3-mock"
    base.mkdir(parents=True, exist_ok=True)
    return base


def acquire_lock() -> bool:
    """Acquire lock for this instance if available or expired."""
    try:
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


def upload_file(local_path: str | Path, key: str) -> str:
    """Upload local file to mock S3 key path."""
    try:
        global _lock_acquired
        if not _lock_acquired:
            raise AppError("Lock not acquired before uploading file to s3", "LOCK_NOT_ACQUIRED", context={"local_path": local_path, "key": key})
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
        global _lock_acquired
        if not _lock_acquired:
            raise AppError("Lock not acquired before downloading file from s3", "LOCK_NOT_ACQUIRED", context={"local_path": local_path, "key": key})
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


def file_exists(key: str) -> bool:
    """Check whether a key exists in mock S3."""
    global _lock_acquired
    if not _lock_acquired:
        raise AppError("Lock not acquired before checking file existence in s3", "LOCK_NOT_ACQUIRED", context={"key": key})
    return (_mock_dir() / key).exists()


def delete_file(key: str) -> bool:
    """Delete a key from mock S3 if present."""
    global _lock_acquired
    if not _lock_acquired:
        raise AppError("Lock not acquired before deleting file from s3", "LOCK_NOT_ACQUIRED", context={"key": key})
    path = _mock_dir() / key
    if path.exists():
        path.unlink()
        return True
    return False


def lock_acquired() -> bool:
    """Check if the lock is currently acquired by this instance."""
    return _lock_acquired
