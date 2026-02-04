"""Parsing helpers for NTE pipelines."""

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.constants import NTE_BASE_URL, NO_PREFIX_VARIANTS, DAYS_MAP
from app.core.errors import AppError
from app.scrape.parse import deptify

_EXTRA_DEPARTMENT_LINKS: tuple[str, str] = (
    "https://muhfd.metu.edu.tr/en/computer-education-and-instructional-technology",
    "https://muhfd.metu.edu.tr/en/meslek-yuksek-okulu-myo",
)
_DAY_BY_INDEX: dict[int, str] = {index: day for day, index in DAYS_MAP.items()}

# NTE List parsing functions

def extract_department_links(soup: BeautifulSoup, department_links: list[str]) -> None:
    """Extract and deduplicate NTE department page links into the provided output list."""
    try:
        discovered: list[str] = []
        for anchor in soup.find_all("a"):
            href = anchor.get("href", "")
            if isinstance(href, str) and "department-" in href:
                discovered.append(urljoin(f"{NTE_BASE_URL}/en/", href))

        discovered.extend(_EXTRA_DEPARTMENT_LINKS)

        seen: set[str] = set()
        for link in discovered:
            if link and link not in seen:
                seen.add(link)
                department_links.append(link)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to extract department links.",
            "EXTRACT_DEPARTMENT_LINKS_FAILED",
            cause=e,
        )
        raise err


def extract_courses(
    soup: BeautifulSoup,
    courses: list[dict[str, str]],
) -> str:
    """Extract department name and course rows from a department page table."""
    try:
        dept_name = ""
        header_el = soup.find("h1")
        if header_el:
            dept_name = header_el.get_text(strip=True)

        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue
                code = cols[0].get_text(strip=True)
                name = cols[1].get_text(strip=True)
                credits = cols[2].get_text(strip=True)
                courses.append(
                    {
                        "code": code,
                        "name": name,
                        "credits": credits,
                    }
                )

        return dept_name
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to extract courses from department page.",
            "NTE_EXTRACT_COURSES_FAILED",
            cause=e,
        )
        raise err

# NTE Available parsing functions

def _is_available_section(section: dict[str, Any]) -> bool:
    """Return True when section has no constraints or is open to all departments."""
    _ALLOWED = {"ALL", "TUM", "TÜM"}
    constraints = section.get("c", [])
    if not constraints:
        return True
    for item in constraints:
        dept_text = str(item.get("d", "")).strip().upper()
        if not dept_text:
            continue
        if any(allowed in dept_text for allowed in _ALLOWED):
            return True
    return False

def build_available_index(
    courses: dict[str, Any],
    dept_map: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Build index of available courses keyed by prefixed course code."""
    try:
        index: dict[str, dict[str, str]] = {}

        for course_code, course_node in courses.items():
            if not isinstance(course_node, dict):
                continue
            sections = course_node.get("Sections", {})
            if not isinstance(sections, dict):
                sections = {}
            
            if not any(_is_available_section(s) for s in sections.values()):
                continue
            course_code_str = str(course_code)
            dept_code = course_code_str[:3]
            dept_meta = dept_map.get(dept_code, {})
            dept_prefix = dept_meta.get("p", "") if isinstance(dept_meta, dict) else ""
            if not dept_prefix or dept_prefix in NO_PREFIX_VARIANTS:
                continue
            prefixed_course_code = deptify(dept_prefix, course_code_str)
            course_name = str(course_node.get("Course Name", ""))
            
            index[prefixed_course_code] = {
                "numeric": course_code_str,
                "name": course_name
            }

        return index
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to build available courses index.",
            "BUILD_AVAILABLE_INDEX_FAILED",
            cause=e,
        )
        raise err
    
def extract_nte_courses(nte_data: dict[str, list[dict[str, str]]], nte_courses: list[dict[str, str]]) -> None:
    """Flatten NTE list by departments into unique course rows by prefixed code."""
    try:
        course_codes_seen: set[str] = set()
        for dept_courses in nte_data.values():
            for course in dept_courses:
                code = str(course.get("code", "")).strip().upper().replace(" ", "")
                if not code or code in course_codes_seen:
                    continue
                course_codes_seen.add(code)
                nte_courses.append(course)
        if not nte_courses:
            raise AppError("Extracted NTE courses list is empty.", "NTE_AVAILABLE_NO_NTE_COURSES")
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to extract NTE courses from NTE list data.",
            "NTE_AVAILABLE_EXTRACT_COURSES_FAILED",
            cause=e,
        )
        raise err
    
def build_course_output(
    course_code: str,
    prefixed_code: str,
    course_name: str,
    credits: str,
    courses_data: dict[str, Any],
) -> dict[str, Any]:
    """Build output course node with available sections only."""
    try:
        course_node = courses_data.get(course_code, {})
        if not isinstance(course_node, dict):
            course_node = {}
        sections = course_node.get("Sections", {})
        if not isinstance(sections, dict):
            sections = {}
        
        output_sections: list[dict[str, Any]] = []
        
        for section_id, section in sections.items():
            if not isinstance(section, dict):
                continue
            if not _is_available_section(section):
                continue
            
            times = section.get("t", [])
            if not times:
                time_list = [{"day": "No Timestamp Added Yet"}]
            else:
                time_list: list[dict[str, str]] = []
                for time_slot in times:
                    if not isinstance(time_slot, dict):
                        continue
                    day_num = time_slot.get("d", "")
                    day = _DAY_BY_INDEX.get(day_num, "no day info") if isinstance(day_num, int) else "no day info"
                    time_list.append({
                        "day": day,
                        "start": time_slot.get("s", ""),
                        "end": time_slot.get("e", ""),
                        "room": time_slot.get("p", "")
                    })
            
            instructors = section.get("i", [])
            if not isinstance(instructors, list):
                instructors = []
            
            output_sections.append({
                "section_id": section_id,
                "times": time_list,
                "instructors": instructors
            })
        
        if not output_sections:
            output_sections = [{
                "section_id": "not found",
                "times": [{"day": "No Timestamp Added Yet"}],
                "instructors": []
            }]
        
        return {
            "code": {
                "departmental": prefixed_code,
                "numeric": course_code,
                "matched_by": "prefixed"
            },
            "name": course_name,
            "credits": credits,
            "sections": output_sections
        }
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to build course output.",
            "BUILD_COURSE_OUTPUT_FAILED",
            cause=e,
        )
        raise err
