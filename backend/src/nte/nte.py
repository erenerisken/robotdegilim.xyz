import logging
from typing import Dict, Any, Optional

from backend.src.errors import AbortNteError
from src.config import app_constants
from src.nte.io import load_data, load_departments, load_nte_list, write_nte_available
from src.utils.s3 import upload_to_s3

logger = logging.getLogger(app_constants.log_nte)

DAY_MAP = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}


def deptify(prefix: str, full_code: str) -> str:
    """Convert numeric course code to prefixed format."""
    return prefix + (full_code[4:] if len(full_code) >= 4 and full_code[3] == "0" else full_code[3:])


def get_prefixed_code(numeric_code: str, dept_map: Dict[str, Any]) -> Optional[str]:
    """Get prefixed course code from numeric code using department mapping."""
    dept_id = numeric_code[:3]
    dept_info = dept_map.get(dept_id, {})
    prefix = dept_info.get("p")
    
    if not prefix or prefix == "-no course-":
        return None
    
    return deptify(prefix, numeric_code)


def is_available_section(section: Dict[str, Any]) -> bool:
    """Check if section is available (no constraints or has 'ALL' constraint)."""
    constraints = section.get("c", [])
    return (not constraints) or any(item.get("d") == "ALL" for item in constraints)


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
                day = DAY_MAP.get(day_num, "no day info") if isinstance(day_num, int) else "no day info"
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


def run_nte():
    """Main NTE processing function."""
    try:
        logger.info("Starting NTE processing.")
        courses_data = load_data()
        departments_data = load_departments()
        nte_data = load_nte_list()
        
        # Build available courses index
        logger.info("Building available courses index.")
        available_index = build_available_index(courses_data, departments_data)
        
        matched = 0
        missed = 0
        output = []
                
        # Handle both dict and list formats for NTE data
        if isinstance(nte_data, dict):
            iterable = (course for course_list in nte_data.values() for course in course_list)
        else:
            iterable = iter(nte_data)
        
        for course in iterable:
            raw_code = (course.get("code") or course.get("Code") or "").strip()
            credits = course.get("credits") or course.get("Credits") or ""
            
            # Normalize code (remove spaces)
            normalized_code = raw_code.replace(" ", "")
            
            # Check if course is available
            course_info = available_index.get(normalized_code)
            if not course_info:
                missed += 1
                continue
            
            # Build course output
            course_output = build_course_output(
                course_info["numeric"],
                normalized_code,
                course_info["name"],
                credits,
                courses_data
            )
            
            output.append(course_output)
            matched += 1
        
        output_path = write_nte_available(output)
        
        # Upload to S3
        upload_to_s3(str(output_path), app_constants.nte_available_json)
        
        logger.info(f"NTE processing completed successfully. Matched: {matched}, Missed: {missed}")
        
    except Exception as e:
        raise AbortNteError(f"NTE processing failed, error: {str(e)}") from e