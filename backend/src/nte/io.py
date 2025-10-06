import logging
from pathlib import Path
from typing import List, Dict, Any

from src.config import app_constants
from src.utils.io import load_json_local_then_s3, write_json
from src.errors import AbortNteAvailableError, AbortNteListError

logger = logging.getLogger(app_constants.log_nte_available)

def write_nte_available(nte_data: List[Dict[str, Any]]) -> Path:
    """Write NTE available courses to JSON file and return path."""
    try:
        output_path = app_constants.data_dir / app_constants.nte_available_json
        write_json(nte_data, output_path)
        return output_path
    except Exception as e:
        raise AbortNteAvailableError(f"Failed to write NTE available courses, error: {str(e)}") from e

def write_nte_list(nte_list: Dict[str, List[Dict[str, Any]]]) -> Path:
    """Write raw NTE list (by department) to JSON and return path."""
    try:
        output_path = app_constants.data_dir / app_constants.nte_list_json
        write_json(nte_list, output_path)
        return output_path
    except Exception as e:
        raise AbortNteListError(f"Failed to write NTE list, error: {str(e)}") from e

def load_data() -> Dict[str, Any]:
    """Load data.json used by nte.

    Returns an object mapping course codes to course info. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    data = load_json_local_then_s3(
        app_constants.data_dir / app_constants.data_json,
        app_constants.data_json,
        label="data",
        logger=logger,
    )
    if not data:
        raise AbortNteAvailableError("Failed to load data.json or it is empty.")
    return data

def load_departments() -> Dict[str, Any]:
    """Load departments.json used by nte.

    Returns an object mapping department codes to metadata. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    data = load_json_local_then_s3(
        app_constants.data_dir / app_constants.departments_json,
        app_constants.departments_json,
        label="departments",
        logger=logger,
    )
    if not data:
        raise AbortNteAvailableError("Failed to load departments.json or it is empty.")
    return data

def load_nte_list() -> Dict[str, Any]:
    """Load nte_list.json used by nte.

    Returns an object mapping department to NTE courses and their informations. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    data = load_json_local_then_s3(
        app_constants.data_dir / app_constants.nte_list_json,
        app_constants.nte_list_json,
        label="nte_list",
        logger=logger,
    )
    if not data:
        raise AbortNteAvailableError("Failed to load nte_list.json or it is empty.")
    return data