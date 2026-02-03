"""I/O helpers for NTE available pipeline dependencies and outputs."""

from typing import Any

from app.core.constants import DEPARTMENTS_FILE, NTE_LIST_FILE, DATA_FILE
from app.core.errors import AppError
from app.core.paths import downloaded_path
from app.storage.local import read_json
from app.storage.s3 import download_file, s3_file_exists


def download_dependencies() -> None:
    """Download departments, nte list, and data artifacts from S3 into the local downloaded directory."""
    try:
        exists=s3_file_exists(DEPARTMENTS_FILE) and s3_file_exists(NTE_LIST_FILE) and s3_file_exists(DATA_FILE)
        if not exists:
            raise AppError("One or more dependencies do not exist in S3", "DOWNLOAD_DEPENDENCIES_FAILED")
        download_file(DEPARTMENTS_FILE, downloaded_path(DEPARTMENTS_FILE))
        download_file(NTE_LIST_FILE, downloaded_path(NTE_LIST_FILE))
        download_file(DATA_FILE, downloaded_path(DATA_FILE))
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to download dependencies",
            "DOWNLOAD_DEPENDENCIES_FAILED",
            cause=e,
        )
        raise err


def load_dependencies() -> dict[str, dict[str, Any]]:
    """Load downloaded departments, nte list, and data JSON and validate it as a non-empty mapping."""
    try:
        download_dependencies()
        departments = read_json(downloaded_path(DEPARTMENTS_FILE))
        nte_list = read_json(downloaded_path(NTE_LIST_FILE))
        data = read_json(downloaded_path(DATA_FILE))
        valid=departments and nte_list and data
        vadid= valid and isinstance(departments, dict) and isinstance(nte_list, list) and isinstance(data, dict)
        if not vadid:
            raise AppError("Dependencies data loading failed", "LOAD_DEPENDENCIES_FAILED")
        return {
            "departments": departments,
            "nte_list": nte_list,
            "data": data,
        }
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to load dependencies data",
            "LOAD_DEPENDENCIES_FAILED",
            cause=e,
        )
        raise err
