import os
import logging
from typing import Dict, Any

from src.config import app_constants
from src.utils.io import write_json, load_json_local_then_s3


logger = logging.getLogger(app_constants.log_musts)


def load_departments() -> Dict[str, Any]:
    """Load departments.json used by musts.

    Returns an object mapping department codes to metadata. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    return load_json_local_then_s3(
        app_constants.data_dir / app_constants.departments_json,
        app_constants.departments_json,
        label="departments",
        logger=logger,
    )


def write_musts(data: Dict[str, Any]) -> str:
    """Write musts.json to the export folder; returns the written path.

    Ensures parent directory exists and writes UTF-8 indented JSON. Raises
    RecoverError on failure.
    """
    path = app_constants.data_dir / app_constants.musts_json
    write_json(data, path)
    return str(path)
