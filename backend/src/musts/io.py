import json
import os
import logging
from typing import Dict, Any

from config import app_constants
from errors import RecoverError


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
    path = app_constants.data_dir / app_constants.departments_json
    data = _load_json_safe(path)
    if data:
        logger.info(f"departments loaded: count={len(data)} file={os.path.basename(path)}")
    return data


def write_musts(data: Dict[str, Any]) -> str:
    """Write musts.json to the export folder; returns the written path.

    Ensures parent directory exists and writes UTF-8 indented JSON. Raises
    RecoverError on failure.
    """
    path = app_constants.data_dir / app_constants.musts_json
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=4)
        return path
    except Exception as e:
        raise RecoverError("Failed to write musts", {"path": path, "error": str(e)}) from None
