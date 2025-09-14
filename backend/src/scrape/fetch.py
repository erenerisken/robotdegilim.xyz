import logging
from bs4 import BeautifulSoup
import requests
from requests import Response

from config import app_constants
from utils.http import get as http_get, post_oibs, get_catalog


logger = logging.getLogger(app_constants.log_scrape)


def get_main_page(session: requests.Session) -> Response:
    response: Response = http_get(session, app_constants.oibs64_url, name="main_page")
    response.encoding = "utf-8"
    return response


def get_dept(session: requests.Session, dept_code: str, semester_code: str, tries: int = 5) -> Response:
    data = {
        "textWithoutThesis": 1,
        "select_dept": dept_code,
        "select_semester": semester_code,
        "submit_CourseList": "Submit",
        "hidden_redir": "Login",
    }
    response: Response = post_oibs(session, data, tries=tries, base_delay=0.9, name="get_dept")
    response.encoding = "utf-8"
    return response


def get_course(session: requests.Session, course_code: str, tries: int = 5) -> Response:
    data = {
        "SubmitCourseInfo": "Course Info",
        "text_course_code": course_code,
        "hidden_redir": "Course_List",
    }
    response: Response = post_oibs(session, data, tries=tries, base_delay=0.9, name="get_course")
    response.encoding = "utf-8"
    return response


def get_section(session: requests.Session, section_code: str, tries: int = 5) -> Response:
    data = {"submit_section": section_code, "hidden_redir": "Course_Info"}
    response: Response = post_oibs(session, data, tries=tries, base_delay=0.9, name="get_section")
    response.encoding = "utf-8"
    return response


def get_department_prefix(session: requests.Session, dept_code: str, course_code: str):
    try:
        response = get_catalog(session, dept_code, course_code, tries=5, base_delay=1.0)
        response.encoding = "utf-8"
        catalog_soup = BeautifulSoup(response.text, "html.parser")
        h2 = catalog_soup.find("h2")
        course_code_with_prefix = h2.get_text().split(" ")[0]
        dept_prefix = "".join([char for char in course_code_with_prefix if char.isalpha()])
        if dept_prefix:
            return dept_prefix
    except Exception as e:
        logger.warning(f"Error getting dept prefix for {dept_code}-{course_code}: {e}")
        return None
