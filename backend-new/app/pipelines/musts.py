import logging
from bs4 import BeautifulSoup

from app.core.settings import get_settings
from app.core.paths import cache_path, staged_path, published_path
from app.core.constants import RequestType, MUSTS_CACHE_FILE, LOGGER_MUSTS, NO_PREFIX_VARIANTS, MUSTS_FILE, LOGGER_ERROR
from app.core.logging import log_item
from app.utils.cache import CacheStore
from app.musts.io import load_departments
from app.musts.fetch import get_department_catalog_page
from app.core.errors import AppError
from app.storage.local import write_json, move_file
from app.storage.s3 import upload_file
from app.api.schemas import ResponseModel
from app.musts.parse import extract_dept_node

def run_musts():
    try:
        settings = get_settings()
        cache = CacheStore(path=cache_path(MUSTS_CACHE_FILE), parser_version=settings.MUSTS_PARSER_VERSION)
        cache.load()

        log_item(LOGGER_MUSTS, logging.INFO, "Musts process started.")
        
        departments = load_departments()

        data = {}
        dept_codes = list(departments.keys())
        dept_len = len(dept_codes)
        for index, dept_code in enumerate(dept_codes, start=1):
            if ( not departments[dept_code].get("p",None) or departments[dept_code]["p"] in NO_PREFIX_VARIANTS ):
                continue
            prefix=departments[dept_code]["p"]

            cache_key, html_hash, response = get_department_catalog_page(dept_code)
            parsed=cache.get(cache_key, html_hash)

            dept_node={}
            if parsed:
                dept_node=parsed["dept_node"]
            else:
                dept_soup = BeautifulSoup(response.text, "html.parser")
                dept_node = extract_dept_node(dept_soup)
                cache.set(cache_key, html_hash, {"dept_node": dept_node})
            
            data[prefix] = dept_node

            if index % 10 == 0:
                progress = (index / dept_len) * 100
                log_item(LOGGER_MUSTS, logging.INFO, f"completed {progress:.2f}% ({index}/{dept_len})")
        
        if not data:
            raise AppError("Musts process produced no course data.", "MUSTS_NO_DATA")
        
        cache.flush()

        musts_path = staged_path(MUSTS_FILE)
        musts_published_path = published_path(MUSTS_FILE)

        write_json(musts_path, data)
        upload_file(musts_path, MUSTS_FILE)
        move_file(musts_path, musts_published_path)

        log_item(LOGGER_MUSTS, logging.INFO, "Musts process completed successfully and files uploaded to S3.")
        return ResponseModel(request_type=RequestType.MUSTS, status="SUCCESS", message="Musts process completed successfully and files uploaded to S3."), 200
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Musts process failed.", "MUSTS_PROCESS_FAILED", cause=e)
        if err.code and "DEPARTMENTS_FAILED" in err.code:
            log_item(LOGGER_MUSTS, logging.ERROR, err)
            status_code = 503
        else:
            log_item(LOGGER_ERROR, logging.ERROR, err)
            status_code = 500
        return ResponseModel(request_type=RequestType.MUSTS, status="FAILED", message="Musts process failed, see the error logs for details."), status_code