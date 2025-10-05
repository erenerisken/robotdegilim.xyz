import logging
import requests

from src.config import app_constants
from src.errors import AbortMustsError
from src.utils.http import get


logger = logging.getLogger(app_constants.log_musts)


def get_department_page(dept_code: str) -> requests.Response:
    try:
        url = app_constants.department_catalog_url.replace("{dept_code}", str(dept_code))
        resp = get(url, name="dept_get")
        resp.encoding = "utf-8"
        return resp
    except Exception as e:
        raise AbortMustsError(f"Failed to get department page, dept_code: {dept_code}, error: {str(e)}") from e
