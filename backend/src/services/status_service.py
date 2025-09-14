import json
import os
from typing import Dict

from app_constants import app_constants
from ops.exceptions import RecoverException

from utils.s3 import upload_to_s3


def write_status(status: Dict[str, str]) -> str:
    """Write status.json to the export folder and return its path."""
    data_path = os.path.join(app_constants.export_folder, app_constants.status_out_name)
    try:
        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(status, data_file, ensure_ascii=False, indent=4)
            return data_path
    except Exception as e:
        raise RecoverException("Failed to export status", {"error": str(e)}) from None


def set_busy(s3_client) -> str:
    path = write_status({"status": "busy"})
    upload_to_s3(s3_client, path, app_constants.status_out_name)
    return path


def set_idle(s3_client) -> str:
    path = write_status({"status": "idle"})
    upload_to_s3(s3_client, path, app_constants.status_out_name)
    return path

