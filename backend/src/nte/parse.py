from typing import Any, Dict, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.config import app_constants
from src.errors import AbortNteListError


def extract_department_links(soup: BeautifulSoup, department_links: list[str]):
    try:
        links=soup.find_all('a')
        if links:
            for link in links:
                href = link.get('href', '')
                # Ör: href="department-architecture"
                if "department-" in href:
                    # /en/ ifadesi gerekebilir, urljoin ile birleştiriyoruz:
                    full_url = urljoin(app_constants.nte_base_url + "/en/", href)
                    department_links.append(full_url)
            try:
                department_links.append("https://muhfd.metu.edu.tr/en/computer-education-and-instructional-technology")
            except:
                pass

            try:
                department_links.append("https://muhfd.metu.edu.tr/en/meslek-yuksek-okulu-myo")
            except:
                pass
    except Exception as e:
        raise AbortNteListError(f"Failed to extract department links, error: {str(e)}") from e
    
def extract_courses(soup: BeautifulSoup, courses:list[dict]) -> str:
    try:
        # 1) Departman adını al
        header_el = soup.find('h1', id='page-title')
        if header_el:
            department_name = header_el.get_text(strip=True)
        else:
            department_name = "Unknown Department"

        # 2) Tabloyu bul
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')
            # İlk satır tablo başlığı, [1:] ile atlıyoruz
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    code = cols[0].get_text(strip=True)
                    name = cols[1].get_text(strip=True)
                    credits = cols[2].get_text(strip=True)
                    courses.append({
                        "code": code,
                        "name": name,
                        "credits": credits
                    })

        return department_name
    except Exception as e:
        raise AbortNteListError(f"Failed to extract courses, error: {str(e)}") from e
    
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
