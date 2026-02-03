from typing import Any, Dict, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.config import app_constants
from src.errors import AbortNteListError
    
    
def _deptify(prefix: str, full_code: str) -> str:
    """Convert numeric course code to prefixed format."""
    return prefix + (full_code[4:] if len(full_code) >= 4 and full_code[3] == "0" else full_code[3:])

def get_prefixed_code(numeric_code: str, dept_map: Dict[str, Any]) -> Optional[str]:
    """Get prefixed course code from numeric code using department mapping."""
    dept_id = numeric_code[:3]
    dept_info = dept_map.get(dept_id, {})
    prefix = dept_info.get("p")
    
    if not prefix or prefix == "-no course-":
        return None
    
    return _deptify(prefix, numeric_code)

def is_available_section(section: Dict[str, Any]) -> bool:
    """A section is available if it has no constraints or explicitly allows all departments.

    We normalize the department text to be robust against whitespace/casing and accept
    common variants that indicate no restriction (e.g., "ALL", "ALL PROGRAMS").
    """
    constraints = section.get("c") or []
    if not constraints:
        return True
    for item in constraints:
        dept_text = str(item.get("d", "")).strip().upper()
        if not dept_text:
            continue
        if dept_text == "ALL" or "ALL" in dept_text or "TUM" in dept_text or "TÜM" in dept_text:
            return True
    return False

def build_available_index(courses: Dict[str, Any], dept_map: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Build index of available courses with prefixed codes.
    Returns: {"ARCH440": {"numeric": "1200440", "name": "ARCH440 - ..."}}
    """
    index = {}
    
    for numeric_id, course in courses.items():
        sections = course.get("Sections", {}) or {}
        
        # Check if course has any available sections
        if not any(is_available_section(s) for s in sections.values()):
            continue
        
        prefixed_code = get_prefixed_code(str(numeric_id), dept_map)
        if not prefixed_code:
            continue
        
        course_name = course.get("Course Name", "") or ""
        
        index[prefixed_code] = {
            "numeric": str(numeric_id),
            "name": course_name
        }
    
    return index

def build_course_output(numeric_id: str, prefixed_code: str, display_name: str, 
                       credits: str, courses: Dict[str, Any]) -> Dict[str, Any]:
    """Build course output with only available sections."""
    course = courses.get(numeric_id, {}) or {}
    sections = course.get("Sections", {}) or {}
    
    output_sections = []
    
    for section_id, section in sections.items():
        if not is_available_section(section):
            continue
        
        # Process times
        times = section.get("t", []) or []
        if not times:
            time_list = [{"day": "No Timestamp Added Yet"}]
        else:
            time_list = []
            for time_slot in times:
                day_num = time_slot.get("d")
                day = app_constants.DAY_MAP.get(day_num, "no day info") if isinstance(day_num, int) else "no day info"
                time_list.append({
                    "day": day,
                    "start": time_slot.get("s", ""),
                    "end": time_slot.get("e", ""),
                    "room": time_slot.get("p", "")
                })
        
        # Process instructors
        instructors = section.get("i", []) or []
        
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
            "numeric": numeric_id,
            "matched_by": "prefixed"
        },
        "name": display_name,
        "credits": credits,
        "sections": output_sections
    }
