import json
from typing import Dict
import boto3

from config import app_constants
from errors import RecoverError
from utils.s3 import upload_to_s3


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
        raise RecoverError("Failed to export status", {"error": str(e)}) from None

def set_busy(s3_client:boto3.client) -> str:
    # Preserve existing flags if possible
    current = get_status(s3_client)
    current["status"] = "busy"
    path = write_status(current)
    upload_to_s3(s3_client, path, app_constants.status_json)
    return path

def set_idle(s3_client:boto3.client) -> str:
    current = get_status(s3_client)
    current["status"] = "idle"
    path = write_status(current)
    upload_to_s3(s3_client, path, app_constants.status_json)
    return path

def get_status(s3_client:boto3.client) -> dict:
    try:
        obj = s3_client.get_object(Bucket=app_constants.s3_bucket_name, Key=app_constants.status_json)
        data = obj['Body'].read().decode('utf-8')
        parsed = json.loads(data)
    except Exception:
        parsed = {}
    # defaults
    parsed.setdefault("status", "idle")
    parsed.setdefault("queued_musts", False)
    parsed.setdefault("depts_ready", False)
    return parsed


def set_status(s3_client:boto3.client, **kwargs) -> dict:
    current = get_status(s3_client)
    current.update(kwargs)
    path = write_status(current)
    upload_to_s3(s3_client, path, app_constants.status_json)
    return current


def detect_depts_ready(s3_client:boto3.client) -> bool:
    """Return True if departments_json exists in the bucket."""
    try:
        s3_client.head_object(Bucket=app_constants.s3_bucket_name, Key=app_constants.departments_json)
        return True
    except Exception:
        return False


def init_status(s3_client:boto3.client) -> dict:
    """Initialize status in S3 to safe defaults at startup.

    Defaults:
    - status: idle
    - queued_musts: False
    - depts_ready: detected from presence of departments file
    """
    return set_status(
        s3_client,
        status="idle",
        queued_musts=False,
        depts_ready=detect_depts_ready(s3_client),
    )
