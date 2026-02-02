import json
import shutil
import time
from pathlib import Path

from app.core.settings import get_settings
from app.core.errors import AppError

def _lock_path():
    """Will be deleted in s3-based implementation."""
    base = _mock_dir()
    return base / "lockfile.lock"

def _mock_dir():
    """Will be deleted in s3-based implementation."""
    base = Path(__file__).resolve().parents[2] / "s3-mock"
    base.mkdir(parents=True, exist_ok=True)
    return base

def acquire_lock():
    """Placeholder for actual s3-based mechanism."""
    try:
        lock_file_path = _lock_path()
        current_time = time.time()
        settings= get_settings()
        timeout = float(settings.S3_LOCK_TIMEOUT_SECONDS)

        if not lock_file_path.exists():
            lock = {"owner": settings.S3_LOCK_OWNER_ID, "acquired_at": current_time, "expires_at": current_time + timeout}
            lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
            return True

        lock_data = json.loads(lock_file_path.read_text(encoding="utf-8"))

        if float(lock_data.get("expires_at")) < current_time:
            lock = {"owner": settings.S3_LOCK_OWNER_ID, "acquired_at": current_time, "expires_at": current_time + timeout}
            lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
            return True

        return False
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to acquire lock", "LOCK_ACQUIRE_FAILED", cause=e)
        raise err


def release_lock():
    """Placeholder for actual s3-based mechanism."""
    try:
        lock_file_path = _lock_path()
        settings= get_settings()
        if not lock_file_path.exists():
            return False
        
        lock_data = json.loads(lock_file_path.read_text(encoding="utf-8"))

        if lock_data.get("owner") == settings.S3_LOCK_OWNER_ID:
            lock_file_path.unlink(missing_ok=True)
            return True
        return False
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to release lock", "LOCK_RELEASE_FAILED", cause=e)
        raise err

def upload_file(local_path, key):
    """Placeholder for actual s3-based mechanism."""
    try:
        src = Path(local_path)
        if not src.exists():
            raise AppError("Failed to upload the file to s3","UPLOAD_FILE_FAILED",context={"local_path": local_path, "key": key, "reason": "path does not exist"})
        dst = _mock_dir() / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return str(dst)
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to upload the file to s3","UPLOAD_FILE_FAILED",context={"local_path": local_path, "key": key}, cause=e)
        raise err


def download_file(key, local_path):
    """Placeholder for actual s3-based mechanism."""
    try:
        src = _mock_dir() / key
        if not src.exists():
            raise AppError("Failed to download the file from s3","DOWNLOAD_FILE_FAILED",context={"local_path": local_path, "key": key, "reason": "key does not exist"})
        dst = Path(local_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        return str(dst)
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to download the file from s3","DOWNLOAD_FILE_FAILED",context={"local_path": local_path, "key": key}, cause=e)
        raise err

def file_exists(key):
    """Placeholder for actual s3-based mechanism."""
    return (_mock_dir() / key).exists()


def delete_file(key):
    """Placeholder for actual s3-based mechanism."""
    path = _mock_dir() / key
    if path.exists():
        path.unlink()
        return True
    return False
