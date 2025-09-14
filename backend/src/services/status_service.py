import json
from typing import Dict
import boto3

from config import app_constants
from ops.exceptions import RecoverException
from utils.s3 import upload_to_s3

def write_status(status: Dict[str, str]) -> str:
    """Write status.json to the data folder and return its path."""
    data_path = app_constants.data_dir / app_constants.status_json
    data_path.mkdir(parents=True, exist_ok=True)
    try:
        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(status, data_file, ensure_ascii=False, indent=4)
            return data_path
    except Exception as e:
        raise RecoverException("Failed to export status", {"error": str(e)}) from None

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
