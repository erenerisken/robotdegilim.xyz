import json
import shutil
import time
from pathlib import Path

from app.core.settings import get_setting

def _lock_path():
    """Will be deleted in s3-based implementation."""
    base = Path(__file__).resolve().parents[2] / "s3-mock"
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    return base / "lockfile.lock"

def _mock_dir():
    base = Path(__file__).resolve().parents[2] / "s3-mock"
    base.mkdir(parents=True, exist_ok=True)
    return base

def acquire_lock():
    """Placeholder for actual s3-based mechanism."""
    lock_file_path = _lock_path()
    current_time = time.time()
    timeout = float(get_setting("S3_LOCK_TIMEOUT_SECONDS", 60))

    if not lock_file_path.exists():
        lock = {"owner": "dev1", "acquired_at": current_time, "expires_at": current_time + timeout}
        lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
        return True

    try:
        lock_data = json.loads(lock_file_path.read_text(encoding="utf-8"))
    except Exception:
        lock_data = {}

    if float(lock_data.get("expires_at", 0)) < current_time:
        lock = {"owner": "dev1", "acquired_at": current_time, "expires_at": current_time + timeout}
        lock_file_path.write_text(json.dumps(lock), encoding="utf-8")
        return True

    return False


def release_lock():
    """Placeholder for actual s3-based mechanism."""
    lock_file_path = _lock_path()
    if not lock_file_path.exists():
        return False
    try:
        lock_data = json.loads(lock_file_path.read_text(encoding="utf-8"))
    except Exception:
        lock_data = {}

    if lock_data and lock_data.get("owner") == "dev1":
        lock_file_path.unlink(missing_ok=True)
        return True

    return False


def get_client():
    """Return a mock S3 client (base directory path)."""
    return _mock_dir()


def upload_file(local_path, key):
    """Upload a file to mock S3 with the given key."""
    src = Path(local_path)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    dst = _mock_dir() / key
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return str(dst)


def download_file(key, local_path):
    """Download a file from mock S3 to the given local path."""
    src = _mock_dir() / key
    if not src.exists():
        raise FileNotFoundError(f"Key not found: {key}")
    dst = Path(local_path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return str(dst)


def head(key):
    """Check if a key exists in mock S3."""
    return (_mock_dir() / key).exists()


def delete(key):
    """Delete a key from mock S3."""
    path = _mock_dir() / key
    if path.exists():
        path.unlink()
        return True
    return False
