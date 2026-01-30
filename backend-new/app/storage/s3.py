import json
import time
from pathlib import Path

from app.core.settings import get_setting

def _lock_path():
    """Will be deleted in s3-based implementation."""
    base = Path(__file__).resolve().parents[2] / "s3-mock"
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    return base / "lockfile.lock"


def acquire_lock():
    """Placeholder for actual s3-based locking mechanism."""
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
    """Placeholder for actual s3-based locking mechanism."""
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
