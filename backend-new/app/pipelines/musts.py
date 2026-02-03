"""Musts pipeline orchestrator for building and publishing musts.json."""

import logging
from typing import Any

from bs4 import BeautifulSoup

from app.api.schemas import ResponseModel
from app.core.constants import (
    LOGGER_ERROR,
    LOGGER_MUSTS,
    MUSTS_CACHE_FILE,
    MUSTS_FILE,
    NO_PREFIX_VARIANTS,
    RequestType,
)
from app.core.errors import AppError
from app.core.logging import log_item
from app.core.paths import cache_path, published_path, staged_path
from app.core.settings import get_settings
from app.musts.fetch import get_department_catalog_page
from app.musts.io import load_departments
from app.musts.parse import extract_dept_node
from app.storage.local import move_file, write_json
from app.storage.s3 import upload_file
from app.utils.cache import CacheStore

MUSTS_DEPENDENCY_ERROR_CODES: tuple[str, ...] = (
    "DOWNLOAD_DEPARTMENTS_FAILED",
    "LOAD_DEPARTMENTS_FAILED",
)


def _is_dependency_error(err: AppError) -> bool:
    """Return True when the error or one of its causes is a musts dependency failure."""
    current: Exception | None = err
    while isinstance(current, AppError):
        if current.code in MUSTS_DEPENDENCY_ERROR_CODES:
            return True
        current = current.cause if isinstance(current.cause, Exception) else None
    return False


def run_musts() -> tuple[ResponseModel, int]:
    """Execute musts pipeline and publish musts.json artifact."""
    try:
        settings = get_settings()
        cache = CacheStore(path=cache_path(MUSTS_CACHE_FILE), parser_version=settings.MUSTS_PARSER_VERSION)
        cache.load()

        log_item(LOGGER_MUSTS, logging.INFO, "Musts process started.")
        
        departments: dict[str, dict[str, Any]] = load_departments()

        data: dict[str, dict[int, list[str]]] = {}
        dept_codes = list(departments.keys())
        dept_len = len(dept_codes)
        for index, dept_code in enumerate(dept_codes, start=1):
            dept_meta = departments.get(dept_code, {})
            prefix = dept_meta.get("p")
            if not isinstance(prefix, str) or prefix in NO_PREFIX_VARIANTS:
                continue

            cache_key, html_hash, response = get_department_catalog_page(dept_code)
            parsed: dict[str, Any] | None = cache.get(cache_key, html_hash)

            dept_node: dict[int, list[str]] = {}
            if parsed:
                dept_node = parsed["dept_node"]
            else:
                dept_soup = BeautifulSoup(response.text, "html.parser")
                dept_node = extract_dept_node(dept_soup)
                cache.set(cache_key, html_hash, {"dept_node": dept_node})
            
            data[prefix] = dept_node

            if index % 10 == 0:
                progress = (index / dept_len) * 100
                log_item(LOGGER_MUSTS, logging.INFO, f"completed {progress:.2f}% ({index}/{dept_len})")
        
        if not data:
            raise AppError("Musts process produced no course data.", "MUSTS_NO_DATA")
        
        cache.flush()

        musts_path = staged_path(MUSTS_FILE)
        musts_published_path = published_path(MUSTS_FILE)

        write_json(musts_path, data)
        upload_file(musts_path, MUSTS_FILE)
        move_file(musts_path, musts_published_path)

        log_item(LOGGER_MUSTS, logging.INFO, "Musts process completed successfully and files uploaded to S3.")
        return ResponseModel(
            request_type=RequestType.MUSTS,
            status="SUCCESS",
            message="Musts process completed successfully and files uploaded to S3.",
        ), 200
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Musts process failed.", "MUSTS_PROCESS_FAILED", cause=e)
        if _is_dependency_error(err):
            log_item(LOGGER_MUSTS, logging.ERROR, err)
            status_code = 503
            message = "Departments data could not be loaded from S3."
        else:
            log_item(LOGGER_ERROR, logging.ERROR, err)
            status_code = 500
            message = "Musts process failed, see the error logs for details."
        return ResponseModel(
            request_type=RequestType.MUSTS,
            status="FAILED",
            message=message,
        ), status_code
