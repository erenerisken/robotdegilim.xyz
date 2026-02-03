import logging
from bs4 import BeautifulSoup

from app.core.settings import get_settings
from app.core.constants import (
    LOGGER_ERROR,
    LOGGER_NTE_LIST,
    NTE_LIST_CACHE_FILE,
    NTE_LIST_FILE,
)
from app.utils.cache import CacheStore
from app.core.paths import cache_path, published_path, staged_path
from app.core.logging import log_item
from app.nte.fetch import get_department_page, get_nte_courses
from app.nte.parse import extract_courses, extract_department_links
from app.core.errors import AppError
from app.storage.local import move_file, write_json
from app.storage.s3 import upload_file

def run_nte_list():
    try:
        settings = get_settings()
        cache = CacheStore(path=cache_path(NTE_LIST_CACHE_FILE), parser_version=settings.NTE_LIST_PARSER_VERSION)
        cache.load()

        log_item(LOGGER_NTE_LIST, logging.INFO, "NTE list process started.")

        departments = {}

        cache_key, html_hash, response = get_nte_courses()
        parsed = cache.get(cache_key, html_hash)

        dept_links = []
        if parsed:
            dept_links = parsed["dept_links"]
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            extract_department_links(soup, dept_links)
            if not dept_links:
                raise AppError("Parsed deptartment links are empty.", "NTE_LIST_NO_DEPARTMENT_LINKS")
            cache.set(cache_key, html_hash, {"dept_links": dept_links})
        
        for link in dept_links:
            cache_key, html_hash, response = get_department_page(link)
            parsed = cache.get(cache_key, html_hash)

            courses= []
            dept_name = ""
            if parsed:
                dept_name = parsed["dept_name"]
                courses = parsed["courses"]
            else:
                dept_soup = BeautifulSoup(response.text, "html.parser")
                dept_name = extract_courses(dept_soup, courses)
                cache.set(cache_key, html_hash, {"dept_name": dept_name, "courses": courses})
            
            if not dept_name:
                log_item(LOGGER_NTE_LIST, logging.WARNING, f"Skipping unnamed department page {link}")
                continue
            
            bucket = departments.setdefault(dept_name, set())
            for course in courses:
                code = course.get("code", "")
                name = course.get("name", "")
                credits = course.get("credits", "")
                if not code:
                    continue
                bucket.add((code.strip(), name.strip(), credits.strip()))
        
        final_output = {}
        for dept_name, course_set in departments.items():
            final_output[dept_name] = [
                {"code": code, "name": name, "credits": credits}
                for code, name, credits in sorted(course_set)
            ]
        
        cache.flush()

        path=staged_path(NTE_LIST_FILE)
        path_published = published_path(NTE_LIST_FILE)

        write_json(path, final_output)
        upload_file(path, NTE_LIST_FILE)
        move_file(path, path_published)

        log_item(LOGGER_NTE_LIST, logging.INFO, "NTE List process completed successfully and files uploaded to S3.")
    
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("NTE List process failed.", "NTE_LIST_PROCESS_FAILED", cause=e)
        log_item(LOGGER_ERROR, logging.ERROR, err)
        raise err