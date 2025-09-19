import logging
from pathlib import Path
from typing import List, Dict, Any

from src.config import app_constants
from src.utils.io import load_json_local_then_s3, write_json

logger = logging.getLogger(app_constants.log_nte)

def write_nte_available(nte_data: List[Dict[str, Any]]) -> Path:
    """Write NTE available courses to JSON file and return path."""
    output_path = app_constants.data_dir / app_constants.nte_available_json
    write_json(nte_data, output_path)
    return output_path
    

def load_data() -> Dict[str, Any]:
    """Load data.json used by nte.

    Returns an object mapping course codes to course info. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    return load_json_local_then_s3(
        app_constants.data_dir / app_constants.data_json,
        app_constants.data_json,
        label="courses data",
        logger=logger,
    )

def load_departments() -> Dict[str, Any]:
    """Load departments.json used by nte.

    Returns an object mapping department codes to metadata. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    return load_json_local_then_s3(
        app_constants.data_dir / app_constants.departments_json,
        app_constants.departments_json,
        label="departments",
        logger=logger,
    )

def load_nte_list() -> Dict[str, Any]:
    """Load nte_list.json used by nte.

    Returns an object mapping department to NTE courses and their informations. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    return load_json_local_then_s3(
        app_constants.data_dir / app_constants.nte_list_json,
        app_constants.nte_list_json,
        label="nte_list",
        logger=logger,
    )