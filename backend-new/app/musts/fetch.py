from requests import Response

from app.utils.http import get
from app.core.constants import DEPARTMENT_CATALOG_URL
from app.utils.cache import hash_content, make_key
from app.core.errors import AppError

def get_department_catalog_page(dept_code) -> tuple[str, str, Response]:
    try:
        url=DEPARTMENT_CATALOG_URL.format(dept_code=dept_code)
        response = get(url, name="get_department_catalog_page")
        response.encoding = "utf-8"
        cache_key = make_key("GET", url)
        html_hash = hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to get department catalog page", "GET_DEPARTMENT_CATALOG_PAGE_FAILED",context={"dept_code": dept_code}, cause=e)
        raise err