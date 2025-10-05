import logging
from typing import Dict, Any

from backend.src.errors import AbortMustsError
from src.config import app_constants
from src.utils.io import write_json, load_json_local_then_s3


logger = logging.getLogger(app_constants.log_musts)


def load_departments() -> Dict[str, Any]:
    """Load departments.json used by musts.

    Returns an object mapping department codes to metadata. Missing or invalid
    files return an empty dict. This function does not modify keys or values.
    """
    depts = load_json_local_then_s3(
        app_constants.data_dir / app_constants.departments_json,
        app_constants.departments_json,
        label="departments",
        logger=logger,
    )
    if not depts:
        raise AbortMustsError("Departments data is empty or not loaded correctly.")
    return depts


def write_musts(data: Dict[str, Any]) -> str:
    """Write musts.json to the export folder; returns the written path.

    Ensures parent directory exists and writes UTF-8 indented JSON. Raises
    RecoverError on failure.
    """
    try:
        path = app_constants.data_dir / app_constants.musts_json
        write_json(data, path)
        return str(path)
    except Exception as e:
        raise AbortMustsError(f"Failed to write musts.json, error: {str(e)}") from e