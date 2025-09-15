import json
import os
import logging
from typing import Dict, Any

from src.config import app_constants
from src.errors import RecoverError
from src.utils.s3 import get_s3_client


logger = logging.getLogger(app_constants.log_musts)


def _load_json_safe(path: str) -> Dict[str, Any]:
    """Load a JSON object from path, returning {} on failure and logging once."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.error(f"Failed to load JSON file {path}: {e}")
        return {}


def load_departments() -> Dict[str, Any]:
    """Load departments.json used by musts.

    Returns an object mapping department codes to metadata. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    # 1) Prefer local cache if present (development, or after scrape on same host)
    path = app_constants.data_dir / app_constants.departments_json
    data = _load_json_safe(path)
    if data:
        logger.info(
            f"departments loaded (local): count={len(data)} file={os.path.basename(path)}"
        )
        return data

    # 2) Fallback to S3 to align with status/depts_ready detection
    try:
        s3 = get_s3_client()
        obj = s3.get_object(
            Bucket=app_constants.s3_bucket_name, Key=app_constants.departments_json
        )
        body = obj["Body"].read().decode("utf-8")
        data = json.loads(body)
        if isinstance(data, dict) and data:
            logger.info(
                f"departments loaded (s3): count={len(data)} key={app_constants.departments_json}"
            )
            return data
    except Exception as e:
        # Silent fallback; caller decides on error handling based on empty result
        logger.warning(f"could not load departments from S3: {e}")
    return {}


def write_musts(data: Dict[str, Any]) -> str:
    """Write musts.json to the export folder; returns the written path.

    Ensures parent directory exists and writes UTF-8 indented JSON. Raises
    RecoverError on failure.
    """
    path = app_constants.data_dir / app_constants.musts_json
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=4)
        return str(path)
    except Exception as e:
        raise RecoverError("Failed to write musts", {"path": path, "error": str(e)}) from None
