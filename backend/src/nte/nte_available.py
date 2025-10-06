import logging
from typing import Dict, Iterator, List, Tuple

from src.errors import AbortNteAvailableError
from src.config import app_constants
from src.nte.io import load_data, load_departments, load_nte_list, write_nte_available
from src.utils.s3 import upload_to_s3
from src.nte.parse import build_available_index, build_course_output


logger = logging.getLogger(app_constants.log_nte_available)


def _iter_nte_courses(nte_data: object) -> Iterator[Dict[str, object]]:
    """Yield course dictionaries from supported raw formats."""
    if isinstance(nte_data, dict):
        for course_list in nte_data.values():
            if isinstance(course_list, list):
                for course in course_list:
                    if isinstance(course, dict):
                        yield course
    elif isinstance(nte_data, list):
        for course in nte_data:
            if isinstance(course, dict):
                yield course


def _normalize_code(raw_code: str) -> str:
    return raw_code.replace(" ", "").upper()


def nte_available() -> Tuple[str, Dict[str, int]]:
    """Build and publish `nteAvailable.json` from latest scrape artifacts.

    Returns a tuple of the written file path and a metrics dict for callers/tests.
    """

    try:
        logger.info("nte_available: loading scrape artefacts")
        courses_data = load_data()
        departments_data = load_departments()
        nte_data = load_nte_list()

        logger.info("nte_available: indexing available courses")
        available_index = build_available_index(courses_data, departments_data)
        if not available_index:
            raise AbortNteAvailableError("No available courses found in scrape data.")

        seen_codes: set[str] = set()
        matched = 0
        missed = 0
        output: List[Dict[str, object]] = []

        for course in _iter_nte_courses(nte_data):
            raw_code = str(course.get("code") or course.get("Code") or "").strip()
            if not raw_code:
                missed += 1
                continue
            normalized_code = _normalize_code(raw_code)
            if normalized_code in seen_codes:
                continue

            course_info = available_index.get(normalized_code)
            if not course_info:
                missed += 1
                continue

            credits = str(course.get("credits") or course.get("Credits") or "").strip()
            output.append(
                build_course_output(
                    course_info["numeric"],
                    normalized_code,
                    course_info["name"],
                    credits,
                    courses_data,
                )
            )
            seen_codes.add(normalized_code)
            matched += 1

        # Sort deterministically by departmental code for stable outputs
        output.sort(key=lambda item: item.get("code", {}).get("departmental", ""))

        if not output:
            raise AbortNteAvailableError("No matching NTE courses could be produced from the input data.")

        output_path = write_nte_available(output)
        upload_to_s3(output_path, app_constants.nte_available_json)

        logger.info(
            "nte_available: published %s (matched=%s missed=%s)",
            app_constants.nte_available_json,
            matched,
            missed,
        )

        return str(output_path), {"matched": matched, "missed": missed}

    except AbortNteAvailableError:
        raise
    except Exception as e:
        raise AbortNteAvailableError(f"NTE processing failed, error: {str(e)}") from e