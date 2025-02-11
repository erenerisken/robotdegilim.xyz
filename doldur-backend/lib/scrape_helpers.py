import requests
import json
from bs4 import BeautifulSoup
from lib.constants import *
from lib.exceptions import RecoverException
from lib.helpers import check_delay
import logging
import time

logger=logging.getLogger(shared_logger)

def get_main_page(session: requests.Session):
    """Fetch oibs64 main page using session"""
    try:
        #check_delay()
        response = session.get(oibs64_url, headers=headers)
        response.encoding = "utf-8"
        return response
    except Exception as e:
        raise RecoverException("Failed to get main page",{"error":str(e)}) from None


def get_dept(session: requests.Session, dept_code: str, semester_code: str,tries:int=10):
    """Fetch department page using session with retry mechanism."""
    data = {
        "textWithoutThesis": 1,
        "select_dept": dept_code,
        "select_semester": semester_code,
        "submit_CourseList": "Submit",
        "hidden_redir": "Login",
    }
    attempt=0
    while attempt < tries:
        try:
            check_delay(0.75)
            response = session.post(oibs64_url, headers=headers, data=data)
            response.encoding = "utf-8"
            if response.status_code == 200:
                return response
        except Exception as e:
            raise RecoverException("Failed to get dept page",{"dept_code":dept_code,"error":str(e)}) from None
        attempt+=1
    raise RecoverException("Failed to get dept page",{"trials":tries,"error":str(e)}) from None



def get_course(session: requests.Session, course_code: str,tries:int=10):
    """Fetch course page using session."""
    data = {
        "SubmitCourseInfo": "Course Info",
        "text_course_code": course_code,
        "hidden_redir": "Course_List",
    }
    attempt=0
    while attempt < tries:
        try:
            check_delay(0.75)
            response = session.post(oibs64_url, headers=headers, data=data)
            response.encoding = "utf-8"
            if response.status_code==200:
                return response
        except Exception as e:
            raise RecoverException("Failed to get course page",{"course_code":course_code,"error":str(e)}) from None
        attempt +=1
    raise RecoverException("Failed to get course page",{"course_code":course_code,"trials":tries}) from None

def get_section(session: requests.Session, section_code: str,tries:int=10):
    """Fetch section page using session."""
    data = {"submit_section": section_code, "hidden_redir": "Course_Info"}
    attempt=0
    while attempt < tries:
        try:
            check_delay(0.75)
            response = session.post(oibs64_url, headers=headers, data=data)
            response.encoding = "utf-8"
            if response.status_code == 200:
                return response
        except Exception as e:
            raise RecoverException("Failed to get section page",{"section_code":section_code,"error":str(e)}) from None
        attempt+=1
    raise RecoverException("Failed to get section page",{"section_code":section_code,"trials":tries}) from None


def get_department_prefix(session: requests.Session, dept_code: str, course_code: str):
    """Fetch department prefix from course catalog page with using session"""
    try:
        check_delay()
        response = session.get(
            course_catalog_url.replace("{dept_code}", dept_code).replace(
                "{course_code}", course_code
            ),
            headers=headers,
        )
        response.encoding = "utf-8"
        catalog_soup = BeautifulSoup(response.text, "html.parser")
        h2 = catalog_soup.find("h2")
        if h2:
            course_code_with_prefix = h2.get_text().split(" ")[0]
            dept_prefix = "".join(
                [char for char in course_code_with_prefix if char.isalpha()]
            )
            if dept_prefix:
                return dept_prefix
    except Exception as e:
        raise RecoverException("Failed to get dept prefix",{"dept_code":dept_code,"course_code":course_code,"error":str(e)}) from None


def extract_departments(soup, dept_codes, dept_names):
    """Extract department codes and names from the main page(soup object)."""
    dept_select = soup.find("select", {"name": "select_dept"})
    if dept_select:
        dept_options = dept_select.find_all("option")
        if dept_options:
            for option in dept_options:
                value = option.get("value")
                text = option.get_text()
                if value and text:
                    dept_codes.append(value)
                    dept_names[value] = text


def extract_current_semester(soup):
    """Extract the current semester from the main page(soup object)."""
    semester_select = soup.find("select", {"name": "select_semester"})
    if semester_select:
        current_semester_option = semester_select.find("option")
        if current_semester_option:
            current_semester = tuple(
                (
                    current_semester_option.get("value"),
                    current_semester_option.get_text(),
                )
            )
            return current_semester
    raise RecoverException("Could not extract current semester.") from None

def extract_courses(soup, course_codes, course_names):
    """Extract course codes and names from the department page(soup object)."""
    course_table = soup.find("form").find_all("table")[3]
    course_rows = course_table.find_all("tr")[1:]
    for course_row in course_rows:
        course_cells = course_row.find_all("td")

        course_code = course_cells[0].find("input").get("value")
        course_name = course_cells[2].get_text()

        course_codes.append(course_code)
        course_names[course_code] = course_name

def extract_sections(session: requests.Session, soup, sections):
    """Extract sections and their informations from the course page(soup object)."""
    # The table in the HTML contains nested <tr> tags, meaning there are <tr> elements inside other <tr> elements.
    # This can cause issues when trying to directly parse with BeautifulSoup
    try:
        section_table = soup.find("form").find_all("table")[2]
        section_table_string = str(section_table).replace("\n", "")
        section_rows = extract_tags_as_string(section_table_string, "<tr>", "</tr>")[2:]

        for section_row in section_rows:
            section_node = {}

            time_row = extract_tags_as_string(section_row[4:-5], "<tr>", "</tr>")[0]
            section_info = section_row.replace(time_row, "")
            time_table = extract_tags_as_string(time_row, "<table>", "</table>")[0]

            section_info_soup = BeautifulSoup(section_info, "html.parser")
            time_table_soup = BeautifulSoup(time_table, "html.parser")

            info_cells = section_info_soup.find_all("td")
            time_rows = time_table_soup.find_all("tr")

            section_times = []
            for time_row in time_rows:
                time_cells = time_row.find_all("td")
                if (
                    not time_cells[0].get_text()
                    or time_cells[0].get_text() not in days_dict
                ):
                    continue
                section_times.append(
                    {
                        "p": time_cells[3].find("font").get_text(),
                        "s": time_cells[1].find("font").get_text(),
                        "e": time_cells[2].find("font").get_text(),
                        "d": days_dict[time_cells[0].get_text()],
                    }
                )

            section_code = info_cells[0].find("input").get("value")
            section_instructors = [info_cells[1].get_text(), info_cells[2].get_text()]
            response = get_section(session, section_code)

            section_soup = BeautifulSoup(response.text, "html.parser")
            section_constraints = []
            form_msg = section_soup.find("div", id="formmessage").find("b").get_text()
            if not form_msg:
                extract_constraints(section_soup, section_constraints)

            section_node["i"] = section_instructors
            section_node["c"] = section_constraints
            section_node["t"] = section_times
            sections[section_code] = section_node

    except Exception as e:
        raise RecoverException("Failed to extract sections",{"error":str(e)}) from None

def extract_constraints(soup, constraints):
    """Extracts section constraints from section page(soup object)."""
    try:
        cons_table = soup.find("form").find_all("table")[2]
        cons_rows = cons_table.find_all("tr")[1:]
        for cons_row in cons_rows:
            cons_cells = cons_row.find_all("td")
            constraints.append(
                {
                    "d": cons_cells[0].get_text(),
                    "s": cons_cells[1].get_text(),
                    "e": cons_cells[2].get_text(),
                }
            )
    except Exception as e:
        logger.error(f"Error extracting constraints: {e}")


def any_course(soup):
    """Return True if formmessage contains error message else False"""
    form_msg = soup.find("div", id="formmessage").find("b").get_text()
    if form_msg:
        return False
    return True


def deptify(prefix, course_code):
    """Return course code with prefix"""
    result = "" + prefix
    if course_code[3] == "0":
        result += course_code[4:]
    else:
        result += course_code[3:]
    return result


def extract_tags_as_string(html_code, start_tag, end_tag):
    """Extracts all tags (as string) of an HTML code (given as string) and returns them."""
    stack = []
    tags = []
    sindex = 0
    cindex = 0
    word_length = len(end_tag)
    diff = len(end_tag) - len(start_tag)

    try:
        while cindex < len(html_code):
            if (cindex + word_length) > len(html_code):
                break

            word = html_code[cindex : cindex + word_length]

            if word[:-diff] == start_tag:
                if not stack:
                    sindex = cindex
                stack.append(start_tag)

            if word == end_tag:
                if len(stack) == 1:
                    eindex = cindex + word_length
                    tags.append(html_code[sindex:eindex])
                    stack = []
                elif stack:
                    stack.pop()

            cindex += 1

    except Exception as e:
        raise RecoverException("Failed to extract tags",{"error":str(e)}) from None

    return tags

def write_json(data:dict,file_path):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        raise RecoverException("Failed to write json",{"file_path":file_path,"error":str(e)}) from None
    
def load_prefixes():
    """Find the departments JSON file from export_folder and return its contents as a dictionary."""
    file_path = os.path.join(export_folder, departments_out_name)
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            departments = json.load(file)
            prefixes={}
            for code in departments.keys():
                prefixes[code] = departments[code]['p']
            return prefixes
    except Exception as e:
        logger.error(f"Failed to load prefixes from file {file_path}: {e}")
        return {}