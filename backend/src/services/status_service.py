import json
from typing import Dict, Any, cast
import boto3

from src.config import app_constants
from src.errors import RecoverError
from src.utils.s3 import get_s3_client, upload_to_s3


def write_status(status: Dict[str, str]) -> str:
    """Write status.json to the data folder and return its path."""
    # Ensure directory exists
    app_constants.data_dir.mkdir(parents=True, exist_ok=True)
    data_path = app_constants.data_dir / app_constants.status_json
    try:
        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(status, data_file, ensure_ascii=False, indent=4)
            return str(data_path)
    except Exception as e:
        raise RecoverError(f"Failed to export status, error: {str(e)}") from e


def set_busy() -> str:
    # Preserve existing flags if possible
    current = get_status()
    current["status"] = "busy"
    path = write_status(current)
    upload_to_s3(path, app_constants.status_json)
    return path


def set_idle() -> str:
    current = get_status()
    current["status"] = "idle"
    path = write_status(current)
    upload_to_s3(path, app_constants.status_json)
    return path


def get_status() -> Dict[str, Any]:
    try:
        s3_client = get_s3_client()
        obj = s3_client.get_object(
            Bucket=app_constants.s3_bucket_name, Key=app_constants.status_json
        )
        data = obj["Body"].read().decode("utf-8")
        parsed = cast(Dict[str, Any], json.loads(data))
    except Exception:
        parsed = {}
    # defaults
    parsed.setdefault("status", "idle")
    parsed.setdefault("queued_musts", False)
    parsed.setdefault("depts_ready", False)
    return parsed


def set_status(**kwargs) -> Dict[str, Any]:
    current = get_status()
    current.update(kwargs)
    path = write_status(current)
    upload_to_s3(path, app_constants.status_json)
    return current


def detect_depts_ready() -> bool:
    """Return True if departments data is available.

    Preference order:
    1) Local cache under data directory (non-empty valid JSON dict)
    2) Presence on S3 (head_object succeeds)
    """
    # Prefer local cache for development or when scraper runs on same host
    try:
        local_path = app_constants.data_dir / app_constants.departments_json
        if local_path.exists():
            with open(local_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, dict) and len(data) > 0:
                    return True
    except Exception:
        # Ignore and fall back to S3 check
        pass

    # Fallback to S3 presence
    try:
        s3_client = get_s3_client()
        s3_client.head_object(
            Bucket=app_constants.s3_bucket_name, Key=app_constants.departments_json
        )
        return True
    except Exception:
        return False


def init_status() -> dict:
    """Initialize status in S3 to safe defaults at startup.

    Defaults:
    - status: idle
    - queued_musts: False
    - depts_ready: detected from presence of departments file
    """
    return set_status(
        status="idle",
        queued_musts=False,
        depts_ready=detect_depts_ready(),
    )
