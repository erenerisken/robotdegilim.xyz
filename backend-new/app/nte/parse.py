"""Parsing helpers for NTE pipelines."""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.constants import NTE_BASE_URL, NO_PREFIX_VARIANTS, DAYS_MAP
from app.core.errors import AppError
from app.scrape.parse import deptify

_EXTRA_DEPARTMENT_LINKS: tuple[str, str] = (
    "https://muhfd.metu.edu.tr/en/computer-education-and-instructional-technology",
    "https://muhfd.metu.edu.tr/en/meslek-yuksek-okulu-myo",
)

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


def extract_courses(soup: BeautifulSoup, courses: list[dict[str, str]]) -> str:
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

def _is_available_section(section: Dict[str, Any]) -> bool:
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

def build_available_index(courses: Dict[str, Any], dept_map: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Build index of available courses with prefixed codes.
    Returns: {"ARCH440": {"numeric": "1200440", "name": "ARCH440 - ..."}}
    """
    try:
        index = {}
    
        for course_code, course_node in courses.items():
            sections = course_node.get("Sections", {})
            
            # Check if course has any available sections
            if not any(_is_available_section(s) for s in sections.values()):
                continue
            dept_code= course_code[:3]
            dept_prefix= dept_map.get(dept_code, {}).get("p", "")
            if not dept_prefix or dept_prefix in NO_PREFIX_VARIANTS:
                continue
            prefixed_course_code = deptify(dept_prefix, course_code)
            course_name = course_node.get("Course Name", "")
            
            index[prefixed_course_code] = {
                "numeric": str(course_code),
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
    
def extract_nte_courses(nte_data: object, nte_courses) -> None:
    course_codes_seen: set[str] = set()
    for dept_courses in nte_data.values():
        for course in dept_courses:
            code= str(course.get("code", "")).strip().upper().replace(" ", "")
            if not code or code in course_codes_seen:
                continue
            course_codes_seen.add(code)
            nte_courses.append(course)
    if not nte_courses:
        raise AppError("Extracted NTE courses list is empty.", "NTE_AVAILABLE_NO_NTE_COURSES")
    
def build_course_output(course_code: str, prefixed_code: str, course_name: str, 
                       credits: str, courses_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        course_node = courses_data.get(course_code, {})
        sections = course_node.get("Sections", {})
        
        output_sections = []
        
        for section_id, section in sections.items():
            if not _is_available_section(section):
                continue
            
            # Process times
            times = section.get("t", [])
            if not times:
                time_list = [{"day": "No Timestamp Added Yet"}]
            else:
                time_list = []
                for time_slot in times:
                    day_num = time_slot.get("d", "")
                    day = DAYS_MAP.get(day_num, "no day info")
                    time_list.append({
                        "day": day,
                        "start": time_slot.get("s", ""),
                        "end": time_slot.get("e", ""),
                        "room": time_slot.get("p", "")
                    })
            
            # Process instructors
            instructors = section.get("i", [])
            
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