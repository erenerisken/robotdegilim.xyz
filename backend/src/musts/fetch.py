import logging
import requests

from src.config import app_constants
from src.errors import RecoverError
from src.utils.http import get


logger = logging.getLogger(app_constants.log_musts)


def get_department_page(dept_code: str, tries: int = app_constants.global_retries) -> requests.Response:
    try:
        url = app_constants.department_catalog_url.replace("{dept_code}", str(dept_code))
        resp = get(url, tries=tries, base_delay=1.0, name="dept_get")
        resp.encoding = "utf-8"
        return resp
    except Exception as e:
        raise RecoverError(f"Failed to get department page, dept_code: {dept_code}, error: {str(e)}") from e
