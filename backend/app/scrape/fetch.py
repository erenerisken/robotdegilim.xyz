"""HTTP fetch helpers for scrape pipeline pages and cache metadata."""

from requests import Response

from app.core.constants import COURSE_CATALOG_URL, OIBS64_URL
from app.utils.http import get, post
from app.core.errors import AppError
from app.utils.cache import hash_content, make_key


def get_main_page() -> tuple[str, str, Response]:
    """Fetch the OIBS main page and return cache metadata with response."""
    try:
        response = get(OIBS64_URL, name="get_main_page")
        response.encoding = "utf-8"
        cache_key = make_key("GET", OIBS64_URL)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to get main page", "GET_MAIN_PAGE_FAILED", cause=e)
        raise err


def get_department_page(dept_code: str, semester_code: str) -> tuple[str, str, Response]:
    """Fetch department course list page for the given semester."""
    data = {
        "textWithoutThesis": 1,
        "select_dept": dept_code,
        "select_semester": semester_code,
        "submit_CourseList": "Submit",
        "hidden_redir": "Login",
    }
    try:
        response = post(OIBS64_URL, data=data, name="get_department_page")
        response.encoding = "utf-8"
        cache_key = make_key("POST", OIBS64_URL, data=data)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Failed to get department page",
            code="GET_DEPARTMENT_PAGE_FAILED",
            context={"dept_code": dept_code, "semester_code": semester_code},
            cause=e,
        )
        raise err


def get_course_page(course_code: str) -> tuple[str, str, Response]:
    """Fetch detailed page for a single course."""
    data = {
        "SubmitCourseInfo": "Course Info",
        "text_course_code": course_code,
        "hidden_redir": "Course_List",
    }
    try:
        response = post(OIBS64_URL, data=data, name="get_course_page")
        response.encoding = "utf-8"
        cache_key = make_key("POST", OIBS64_URL, data=data)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Failed to get course page",
            code="GET_COURSE_PAGE_FAILED",
            context={"course_code": course_code},
            cause=e,
        )
        raise err


def get_section_page(section_code: str, course_code: str) -> tuple[str, str, Response]:
    """Fetch detail page for a single section code."""
    data = {"submit_section": section_code, "hidden_redir": "Course_Info"}
    try:
        response = post(OIBS64_URL, data=data, name="get_section_page")
        response.encoding = "utf-8"
        key_data = {
            **data,
            "_course_code": str(course_code),  # cache-only context
        }
        cache_key = make_key("POST", OIBS64_URL, data=key_data)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Failed to get section page",
            code="GET_SECTION_PAGE_FAILED",
            context={"section_code": section_code, "course_code": course_code},
            cause=e,
        )
        raise err


def get_course_catalog_page(dept_code: str, course_code: str) -> tuple[str, str, Response]:
    """Fetch course catalog page used for department prefix detection."""
    try:
        url = COURSE_CATALOG_URL.replace("{dept_code}", dept_code).replace("{course_code}", course_code)
        response = get(url, name="get_course_catalog_page")
        response.encoding = "utf-8"
        cache_key = make_key("GET", url)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Failed to get course catalog page",
            code="GET_COURSE_CATALOG_PAGE_FAILED",
            context={"dept_code": dept_code, "course_code": course_code},
            cause=e,
        )
        raise err
