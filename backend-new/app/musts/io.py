"""I/O helpers for musts pipeline dependencies and outputs."""

from typing import Any

from app.core.constants import DEPARTMENTS_FILE
from app.core.errors import AppError
from app.core.paths import downloaded_path
from app.storage.local import read_json
from app.storage.s3 import download_file, s3_file_exists


def download_departments() -> str:
    """Download departments artifact from S3 into the local downloaded directory."""
    try:
        if not s3_file_exists(DEPARTMENTS_FILE):
            raise AppError("Departments file does not exist in S3", "DOWNLOAD_DEPARTMENTS_FAILED")
        return download_file(DEPARTMENTS_FILE, downloaded_path(DEPARTMENTS_FILE))
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to download departments file",
            "DOWNLOAD_DEPARTMENTS_FAILED",
            cause=e,
        )
        raise err


def load_departments() -> dict[str, dict[str, Any]]:
    """Load downloaded departments JSON and validate it as a non-empty mapping."""
    try:
        download_departments()
        result = read_json(downloaded_path(DEPARTMENTS_FILE))
        if not isinstance(result, dict) or not result:
            raise AppError("Departments data loading failed", "LOAD_DEPARTMENTS_FAILED")
        return result
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to load departments data",
            "LOAD_DEPARTMENTS_FAILED",
            cause=e,
        )
        raise err
