"""Scrape pipeline orchestrator for full data refresh workflow."""

from datetime import datetime
import logging
from typing import Any

import pytz
from bs4 import BeautifulSoup

from app.api.schemas import ResponseModel
from app.core.constants import NO_PREFIX_VARIANTS, RequestType
from app.core.errors import AppError
from app.core.logging import log_item
from app.core.settings import get_path, get_settings
from app.scrape.fetch import (
    get_course_catalog_page,
    get_course_page,
    get_department_page,
    get_main_page,
)
from app.scrape.io import load_local_dept_prefixes
from app.scrape.parse import (
    any_course,
    deptify,
    extract_courses,
    extract_current_semester,
    extract_departments,
    extract_dept_prefix,
    extract_sections,
)
from app.storage.local import move_file, write_json
from app.storage.s3 import upload_file
from app.utils.cache import CacheStore


def run_scrape() -> tuple[ResponseModel, int]:
    """Run full scrape process, publish output files, and return API response."""
    try:
        logger_name = "scrape"
        cache_dir = get_path("DATA_DIR") / "cache"
        settings = get_settings()
        cache = CacheStore(path=cache_dir / "scrape_cache.json", parser_version=settings.SCRAPE_PARSER_VERSION)
        cache.load()

        log_item(logger_name, logging.INFO, "Scraping process started.")

        cache_key, html_hash, response = get_main_page()
        parsed = cache.get(cache_key, html_hash)

        current_semester: tuple[str, str] | None = None
        dept_codes: list[str] = []
        dept_names: dict[str, str] = {}
        if parsed:
            current_semester = parsed["current_semester"]
            dept_codes = parsed["dept_codes"]
            dept_names = parsed["dept_names"]
        else:
            main_soup = BeautifulSoup(response.text, "html.parser")
            extract_departments(main_soup, dept_codes, dept_names)
            current_semester = extract_current_semester(main_soup)
            cache.set(
                cache_key,
                html_hash,
                {
                    "current_semester": current_semester,
                    "dept_codes": dept_codes,
                    "dept_names": dept_names,
                },
            )
        if current_semester is None:
            raise AppError("Current semester could not be determined", "CURRENT_SEMESTER_MISSING")

        department_prefixes = load_local_dept_prefixes()
        data: dict[int, dict[str, Any]] = {}
        dept_len = len(dept_codes)
        for index, dept_code in enumerate(dept_codes, start=1):
            cache_key, html_hash, response = get_department_page(dept_code, current_semester[0])
            parsed = cache.get(cache_key, html_hash)

            course_codes: list[str] = []
            course_names: dict[str, str] = {}
            if parsed:
                course_codes = parsed["course_codes"]
                course_names = parsed["course_names"]
                if len(course_codes) == 0:
                    if dept_code not in department_prefixes:
                        department_prefixes[dept_code] = "<no-course>"
                    continue
            else:
                dept_soup = BeautifulSoup(response.text, "html.parser")
                if not any_course(dept_soup):
                    if dept_code not in department_prefixes:
                        department_prefixes[dept_code] = "<no-course>"
                    cache.set(
                        cache_key,
                        html_hash,
                        {"course_codes": [], "course_names": {}},
                    )
                    continue
                extract_courses(dept_soup, course_codes, course_names)
                cache.set(
                    cache_key,
                    html_hash,
                    {"course_codes": course_codes, "course_names": course_names},
                )
            if len(course_codes) == 0:
                if dept_code not in department_prefixes:
                    department_prefixes[dept_code] = "<no-course>"
                continue

            if dept_code not in department_prefixes or department_prefixes[dept_code] in NO_PREFIX_VARIANTS:
                try:
                    cache_key, html_hash, response = get_course_catalog_page(dept_code, course_codes[0])
                    parsed = cache.get(cache_key, html_hash)

                    dept_prefix = None
                    if parsed:
                        dept_prefix = parsed["dept_prefix"]
                    else:
                        catalog_soup = BeautifulSoup(response.text, "html.parser")
                        dept_prefix = extract_dept_prefix(catalog_soup)
                        if not dept_prefix:
                            dept_prefix = "<prefix-not-found>"
                        cache.set(
                            cache_key,
                            html_hash,
                            {"dept_prefix": dept_prefix},
                        )
                    department_prefixes[dept_code] = dept_prefix
                except Exception as e:
                    err = e if isinstance(e, AppError) else AppError(
                        message="dept_prefix determination failed",
                        code="DEPT_PREFIX_FAILED",
                        context={"dept_code": dept_code},
                        cause=e,
                    )
                    log_item("scrape", logging.WARNING, err)
                    department_prefixes[dept_code] = "<prefix-not-found>"

            for course_code in course_codes:
                cache_key, html_hash, response = get_course_page(course_code)
                parsed = cache.get(cache_key, html_hash)

                course_node: dict[str, Any] = {}
                if parsed:
                    course_node = parsed["course_node"]
                else:
                    course_soup = BeautifulSoup(response.text, "html.parser")
                    sections: dict[str, Any] = {}
                    extract_sections(cache, course_soup, sections)
                    course_node["Course Code"] = course_code
                    if dept_code not in department_prefixes or department_prefixes[dept_code] in NO_PREFIX_VARIANTS:
                        course_node["Course Name"] = (course_code + " - " + course_names[course_code])
                    else:
                        course_node["Course Name"] = (deptify(department_prefixes[dept_code], course_code) + " - " + course_names[course_code])
                    course_node["Sections"] = sections
                    cache.set(
                        cache_key,
                        html_hash,
                        {"course_node": course_node},
                    )
                data[int(course_code)] = course_node
            if index % 10 == 0:
                progress = (index / dept_len) * 100
                log_item("scrape", logging.INFO, f"completed {progress:.2f}% ({index}/{dept_len})")

        cache.flush()

        departments_json: dict[str, dict[str, str]] = {}
        departments_noprefix: dict[str, dict[str, str]] = {}
        for dept_code in dept_codes:
            departments_json[dept_code] = {
                "n": dept_names[dept_code],
                "p": department_prefixes[dept_code],
            }
            if department_prefixes[dept_code] in NO_PREFIX_VARIANTS:
                departments_noprefix[dept_code] = {
                    "n": dept_names[dept_code],
                    "p": department_prefixes[dept_code],
                }
        
        data_dir = get_path("DATA_DIR")
        departments_path = data_dir / "staged" / "departments.json"
        departments_published_path = data_dir / "published" / "departments.json"
        departments_noprefix_path = data_dir / "staged" / "departmentsNoPrefix.json"
        departments_noprefix_published_path = data_dir / "published" / "departmentsNoPrefix.json"
        data_path = data_dir / "staged" / "data.json"
        data_published_path = data_dir / "published" / "data.json"
        last_updated_path = data_dir / "staged" / "lastUpdated.json"
        last_updated_published_path = data_dir / "published" / "lastUpdated.json"

        current_time = datetime.now(pytz.timezone(settings.TIMEZONE))
        formatted_time = current_time.strftime("%d.%m.%Y, %H.%M")
        last_updated_info = {
            "t": current_semester[0] + ":" + current_semester[1],
            "u": formatted_time,
        }

        write_json(departments_path, departments_json)
        write_json(departments_noprefix_path, departments_noprefix)
        write_json(data_path, data)
        write_json(last_updated_path, last_updated_info)

        upload_file(departments_path, "departments.json")
        upload_file(departments_noprefix_path, "departmentsNoPrefix.json")
        upload_file(data_path, "data.json")
        upload_file(last_updated_path, "lastUpdated.json")
        departmentsOverrides_path = data_dir / "raw" / "departmentsOverrides.json"
        if departmentsOverrides_path.exists():
            upload_file(departmentsOverrides_path, "departmentsOverrides.json")

        move_file(departments_path, departments_published_path)
        move_file(departments_noprefix_path, departments_noprefix_published_path)
        move_file(data_path, data_published_path)
        move_file(last_updated_path, last_updated_published_path)

        log_item("scrape", logging.INFO, "Scraping process completed successfully and files uploaded to S3.")
        return ResponseModel(request_type=RequestType.SCRAPE, status="SUCCESS", message="Scraping process completed successfully and files uploaded to S3."), 200
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Scrape process failed",
            code="SCRAPE_PROCESS_FAILED",
            cause=e,
        )
        log_item("error", logging.ERROR, err)
        return ResponseModel(request_type=RequestType.SCRAPE, status="FAILED", message="Scrape process failed, see the error logs for details."), 500
