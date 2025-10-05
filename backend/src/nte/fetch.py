import logging
from requests import Response

from backend.src.errors import AbortNteListError
from src.config import app_constants
from src.utils.http import get as http_get


logger = logging.getLogger(app_constants.log_scrape)

def get_nte_courses() -> Response:
    try:
        response = http_get(app_constants.nte_courses_url, name="nte_courses_page")
        response.encoding = "utf-8"
        return response
    except Exception as e:
        raise AbortNteListError(f"Failed to get nte courses page, error: {str(e)}") from e

def get_department_data(dept_url) -> Response:
    try:
        response = http_get(dept_url, name="nte_department_page")
        response.encoding = "utf-8"
        return response
    except Exception as e:
        raise AbortNteListError(f"Failed to get nte department page, error: {str(e)}") from e