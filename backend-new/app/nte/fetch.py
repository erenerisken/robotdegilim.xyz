
from requests import Response

from app.core.constants import NTE_COURSES_URL
from app.utils.http import get
from app.utils.cache import make_key, hash_content
from app.core.errors import AppError

# NTE List fetching functions

def get_nte_courses() -> tuple[str, str, Response]:
    try:
        response = get(NTE_COURSES_URL, name="get_nte_courses")
        response.encoding = "utf-8"
        cache_key = make_key("GET", NTE_COURSES_URL)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to get NTE courses",
            "GET_NTE_COURSES_FAILED",
            cause=e,
        )
        raise err

def get_department_page(dept_url) -> tuple[str, str, Response]:
    try:
        response = get(dept_url, name="get_nte_department_page")
        response.encoding = "utf-8"
        cache_key = make_key("GET", dept_url)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to get NTE department page",
            "GET_NTE_DEPARTMENT_PAGE_FAILED",
            cause=e,
        )
        raise err