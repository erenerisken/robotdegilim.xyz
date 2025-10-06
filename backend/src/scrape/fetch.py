import logging
from bs4 import BeautifulSoup
from requests import Response

from src.errors import AbortScrapingError
from src.config import app_constants
from src.utils.http import get as http_get, post as http_post


logger = logging.getLogger(app_constants.log_scrape)


def get_main_page() -> Response:
    try:
        response = http_get(app_constants.oibs64_url, name="main_page")
        response.encoding = "utf-8"
        return response
    except Exception as e:
        raise AbortScrapingError(f"Failed to get main page, error: {str(e)}") from e


def get_dept(
    dept_code: str,
    semester_code: str,
) -> Response:
    data = {
        "textWithoutThesis": 1,
        "select_dept": dept_code,
        "select_semester": semester_code,
        "submit_CourseList": "Submit",
        "hidden_redir": "Login",
    }
    try:
        response: Response = http_post(app_constants.oibs64_url, data=data, name="get_dept")
        response.encoding = "utf-8"
        return response
    except Exception as e:
        raise AbortScrapingError(f"Failed to get department {dept_code}, error: {str(e)}") from e


def get_course(course_code: str) -> Response:
    data = {
        "SubmitCourseInfo": "Course Info",
        "text_course_code": course_code,
        "hidden_redir": "Course_List",
    }
    try:
        response: Response = http_post(app_constants.oibs64_url, data=data, name="get_course")
        response.encoding = "utf-8"
        return response
    except Exception as e:
        raise AbortScrapingError(f"Failed to get course {course_code}, error: {str(e)}") from e


def get_section(section_code: str) -> Response:
    data = {"submit_section": section_code, "hidden_redir": "Course_Info"}
    try:
        response: Response = http_post(app_constants.oibs64_url, data=data, name="get_section")
        response.encoding = "utf-8"
        return response
    except Exception as e:
        raise AbortScrapingError(f"Failed to get section {section_code}, error: {str(e)}") from e

def get_department_prefix(dept_code: str, course_code: str):
    try:
        url = app_constants.course_catalog_url.replace("{dept_code}", dept_code).replace(
            "{course_code}", course_code
        )
        response: Response = http_get(url, name="catalog_get")
        response.encoding = "utf-8"
        catalog_soup = BeautifulSoup(response.text, "html.parser")
        h2 = catalog_soup.find("h2")
        course_code_with_prefix = h2.get_text().split(" ")[0]
        dept_prefix = "".join([char for char in course_code_with_prefix if char.isalpha()])
        if dept_prefix:
            return dept_prefix
    except Exception as e:
        logger.warning(f"Error getting dept prefix for {dept_code}-{course_code}, error: {e}")
        return None
