import logging
from typing import Dict, Iterable, List, Set, Tuple

from bs4 import BeautifulSoup

from src.errors import AbortNteListError
from src.config import app_constants
from src.nte.fetch import get_nte_courses, get_department_data
from src.nte.io import write_nte_list
from src.nte.parse import extract_courses, extract_department_links
from src.utils.s3 import upload_to_s3


logger = logging.getLogger(app_constants.log_nte_list)


def _dedupe_links(links: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    ordered: List[str] = []
    for link in links:
        if link and link not in seen:
            seen.add(link)
            ordered.append(link)
    return ordered


def nte_list() -> str:
    """Scrape NTE course listings and persist them locally and on S3."""

    try:
        departments: Dict[str, Set[Tuple[str, str, str]]] = {}

        response = get_nte_courses()
        soup = BeautifulSoup(response.text, "html.parser")
        raw_links: List[str] = []
        extract_department_links(soup, raw_links)
        dept_links = _dedupe_links(raw_links)
        if not dept_links:
            raise AbortNteListError("No department links were discovered on the NTE courses page.")
        logger.info("nte_list: discovered %s department links", len(dept_links))

        for link in dept_links:
            resp = get_department_data(link)
            soup = BeautifulSoup(resp.text, "html.parser")
            courses: List[Dict[str, str]] = []
            dept_name = extract_courses(soup, courses)
            if not dept_name:
                logger.warning("nte_list: skipping unnamed department page %s", link)
                continue

            bucket = departments.setdefault(dept_name, set())
            for course in courses:
                code = course.get("code") or ""
                name = course.get("name") or ""
                credits = course.get("credits") or ""
                if not code:
                    continue
                bucket.add((code.strip(), name.strip(), credits.strip()))

        final_output: Dict[str, List[Dict[str, str]]] = {}
        for dept_name, course_set in departments.items():
            final_output[dept_name] = [
                {"code": code, "name": name, "credits": credits}
                for code, name, credits in sorted(course_set)
            ]

        output_path = write_nte_list(final_output)
        upload_to_s3(str(output_path), app_constants.nte_list_json)
        logger.info(
            "nte_list: exported %s departments to %s",
            len(final_output),
            output_path,
        )

        return str(output_path)

    except AbortNteListError:
        raise
    except Exception as e:
        raise AbortNteListError(f"Failed to process NTE list, error: {str(e)}") from e
