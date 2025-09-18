import logging
from bs4 import BeautifulSoup
import requests
from requests import Response

from src.config import app_constants
from src.utils.http import get as http_get, post


logger = logging.getLogger(app_constants.log_scrape)


def get_main_page(session: requests.Session) -> Response:
    response: Response = http_get(session, app_constants.oibs64_url, name="main_page")
    response.encoding = "utf-8"
    return response


def get_dept(
    session: requests.Session,
    dept_code: str,
    semester_code: str,
    tries: int = app_constants.global_retries,
) -> Response:
    data = {
        "textWithoutThesis": 1,
        "select_dept": dept_code,
        "select_semester": semester_code,
        "submit_CourseList": "Submit",
        "hidden_redir": "Login",
    }
    response: Response = _post_oibs(session, data, tries=tries, base_delay=0.9, name="get_dept")
    response.encoding = "utf-8"
    return response


def get_course(
    session: requests.Session, course_code: str, tries: int = app_constants.global_retries
) -> Response:
    data = {
        "SubmitCourseInfo": "Course Info",
        "text_course_code": course_code,
        "hidden_redir": "Course_List",
    }
    response: Response = _post_oibs(session, data, tries=tries, base_delay=0.9, name="get_course")
    response.encoding = "utf-8"
    return response


def get_section(
    session: requests.Session, section_code: str, tries: int = app_constants.global_retries
) -> Response:
    data = {"submit_section": section_code, "hidden_redir": "Course_Info"}
    response: Response = _post_oibs(session, data, tries=tries, base_delay=0.9, name="get_section")
    response.encoding = "utf-8"
    return response


def get_department_prefix(session: requests.Session, dept_code: str, course_code: str):
    try:
        # Use global retry setting from utils.http defaults
        response = _get_catalog(session, dept_code, course_code, base_delay=1.0)
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


# Local wrappers for scrape flows (not generic):
def _post_oibs(
    session: requests.Session,
    data: dict,
    *,
    tries: int = app_constants.global_retries,
    base_delay: float = 0.9,
    name: str = "oibs_post",
) -> Response:
    return post(
        session, app_constants.oibs64_url, data=data, tries=tries, base_delay=base_delay, name=name
    )


def _get_catalog(
    session: requests.Session,
    dept_code: str,
    course_code: str,
    *,
    tries: int = app_constants.global_retries,
    base_delay: float = 1.0,
) -> Response:
    url = app_constants.course_catalog_url.replace("{dept_code}", dept_code).replace(
        "{course_code}", course_code
    )
    return http_get(session, url, tries=tries, base_delay=base_delay, name="catalog_get")
