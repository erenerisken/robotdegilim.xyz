"""NTE list pipeline orchestrator for building and publishing nteList.json."""

import logging
from typing import Any

from bs4 import BeautifulSoup

from app.core.constants import (
    LOGGER_ERROR,
    LOGGER_NTE_LIST,
    NTE_LIST_CACHE_FILE,
    NTE_LIST_FILE,
)
from app.core.errors import AppError
from app.core.logging import log_item
from app.core.paths import cache_path, published_path, staged_path
from app.core.settings import get_settings
from app.nte.fetch import get_department_page, get_nte_courses
from app.nte.parse import extract_courses, extract_department_links
from app.storage.local import move_file, write_json
from app.storage.s3 import upload_file
from app.utils.cache import CacheStore


def run_nte_list() -> str:
    """Build nteList.json from NTE pages, publish it to S3, and return published path."""
    try:
        settings = get_settings()
        cache = CacheStore(
            path=cache_path(NTE_LIST_CACHE_FILE),
            parser_version=settings.NTE_LIST_PARSER_VERSION,
        )
        cache.load()

        log_item(LOGGER_NTE_LIST, logging.INFO, "NTE list process started.")

        departments: dict[str, set[tuple[str, str, str]]] = {}

        cache_key, html_hash, response = get_nte_courses()
        parsed: dict[str, Any] | None = cache.get(cache_key, html_hash)

        dept_links: list[str] = []
        if parsed:
            dept_links = parsed.get("dept_links", [])
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            extract_department_links(soup, dept_links)
            if not dept_links:
                raise AppError("Parsed department links are empty.", "NTE_LIST_NO_DEPARTMENT_LINKS")
            cache.set(cache_key, html_hash, {"dept_links": dept_links})

        for link in dept_links:
            cache_key, html_hash, response = get_department_page(link)
            parsed = cache.get(cache_key, html_hash)

            courses: list[dict[str, str]] = []
            dept_name = ""
            if parsed:
                dept_name = parsed.get("dept_name", "")
                courses = parsed.get("courses", [])
            else:
                dept_soup = BeautifulSoup(response.text, "html.parser")
                dept_name = extract_courses(dept_soup, courses)
                cache.set(cache_key, html_hash, {"dept_name": dept_name, "courses": courses})

            if not dept_name:
                log_item(LOGGER_NTE_LIST, logging.WARNING, f"Skipping unnamed department page {link}")
                continue

            bucket = departments.setdefault(dept_name, set())
            for course in courses:
                code = str(course.get("code", "")).strip()
                if not code:
                    continue
                name = str(course.get("name", "")).strip()
                credits = str(course.get("credits", "")).strip()
                bucket.add((code, name, credits))

        final_output: dict[str, list[dict[str, str]]] = {}
        for dept_name, course_set in departments.items():
            final_output[dept_name] = [
                {"code": code, "name": name, "credits": credits}
                for code, name, credits in sorted(course_set)
            ]

        if not final_output:
            raise AppError("NTE list process produced no output.", "NTE_LIST_NO_DATA")

        cache.flush()

        path = staged_path(NTE_LIST_FILE)
        path_published = published_path(NTE_LIST_FILE)

        write_json(path, final_output)
        upload_file(path, NTE_LIST_FILE)
        move_file(path, path_published)

        log_item(LOGGER_NTE_LIST, logging.INFO, "NTE list process completed successfully and files uploaded to S3.")
        return str(path_published)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "NTE list process failed.",
            "NTE_LIST_PROCESS_FAILED",
            cause=e,
        )
        log_item(LOGGER_ERROR, logging.ERROR, err)
        raise err
