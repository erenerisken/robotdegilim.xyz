from datetime import datetime
from bs4 import BeautifulSoup
import pytz

from app.core.logging import get_logger
from app.core.settings import get_path, get_setting
from app.scrape.fetch import get_course_catalog_page, get_course_page, get_main_page, get_department_page
from app.scrape.io import load_local_dept_prefixes
from app.scrape.parse import any_course, deptify, extract_courses, extract_current_semester, extract_departments, extract_dept_prefix, extract_sections
from app.utils.cache import CacheStore
from app.core.constants import NO_PREFIX_VARIANTS
from app.storage.local import write_json


def run_scrape():
    try:
        logger = get_logger("scrape")
        cache = CacheStore(parser_version=get_setting("SCRAPE_PARSER_VERSION"))
        cache.load()

        logger.info("Scraping process started.")

        cache_key, html_hash, response = get_main_page()
        parsed = cache.get(cache_key, html_hash)

        current_semester = None
        dept_codes = []
        dept_names = {}
        if parsed:
            current_semester = parsed["current_semester"]
            dept_codes = parsed["dept_codes"]
            dept_names = parsed["dept_names"]
        else:
            main_soup = BeautifulSoup(response.text, "html.parser")
            extract_departments(main_soup, dept_codes, dept_names)
            current_semester = extract_current_semester(main_soup)
            cache.set(
                cache_key,
                html_hash,
                {
                    "current_semester": current_semester,
                    "dept_codes": dept_codes,
                    "dept_names": dept_names,
                },
            )

        department_prefixes = load_local_dept_prefixes()
        data = {}
        dept_len = len(dept_codes)
        for index, dept_code in enumerate(dept_codes, start=1):
            cache_key, html_hash, response = get_department_page(dept_code, current_semester[0])
            parsed = cache.get(cache_key, html_hash)

            course_codes = []
            course_names = {}
            if parsed:
                course_codes = parsed["course_codes"]
                course_names = parsed["course_names"]
                if len(course_codes) == 0:
                    if dept_code not in department_prefixes:
                        department_prefixes[dept_code] = "<no-course>"
                    continue
            else:
                dept_soup = BeautifulSoup(response.text, "html.parser")
                if not any_course(dept_soup):
                    cache.set(
                        cache_key,
                        html_hash,
                        {"course_codes": [], "course_names": {}},
                    )
                    continue
                extract_courses(dept_soup, course_codes, course_names)
                cache.set(
                    cache_key,
                    html_hash,
                    {"course_codes": course_codes, "course_names": course_names},
                )
            if len(course_codes) == 0:
                if dept_code not in department_prefixes:
                    department_prefixes[dept_code] = "<no-course>"
                continue
            
            if(dept_code not in department_prefixes or department_prefixes[dept_code] in NO_PREFIX_VARIANTS):
                cache_key, html_hash, response = get_course_catalog_page(dept_code, course_codes[0])
                parsed = cache.get(cache_key, html_hash)

                dept_prefix = None
                if parsed:
                    dept_prefix = parsed["dept_prefix"]
                else:
                    catalog_soup = BeautifulSoup(response.text, "html.parser")
                    dept_prefix = extract_dept_prefix(catalog_soup)
                    if not dept_prefix:
                        dept_prefix = "<prefix-not-found>"
                    cache.set(
                        cache_key,
                        html_hash,
                        {"dept_prefix": dept_prefix},
                    )
                department_prefixes[dept_code] = dept_prefix

            for course_code in course_codes:
                cache_key, html_hash, response = get_course_page(course_code)
                parsed = cache.get(cache_key, html_hash)
                
                course_node = {}
                if parsed:
                    course_node = parsed["course_node"]
                else:
                    course_soup = BeautifulSoup(response.text, "html.parser")
                    sections = {}
                    extract_sections(cache, course_soup, sections)
                    course_node["Course Code"] = course_code
                    if (dept_code not in department_prefixes or department_prefixes[dept_code] in NO_PREFIX_VARIANTS):
                        course_node["Course Name"] = (course_code + " - " + course_names[course_code])
                    else:
                        course_node["Course Name"] = (deptify(department_prefixes[dept_code], course_code) + " - " + course_names[course_code])
                    course_node["Sections"] = sections
                    cache.set(
                        cache_key,
                        html_hash,
                        {"course_node": course_node},
                    )
                data[int(course_code)] = course_node
            if index % 10 == 0:
                progress = (index / dept_len) * 100
                logger.info(f"completed {progress:.2f}% ({index}/{dept_len})")
                    
        cache.flush()

        departments_json = {}
        departments_noprefix = {}
        for dept_code in dept_codes:
            departments_json[dept_code] = {
                "n": dept_names[dept_code],
                "p": department_prefixes[dept_code],
            }
            if department_prefixes[dept_code] in NO_PREFIX_VARIANTS:
                departments_noprefix[dept_code] = {
                    "n": dept_names[dept_code],
                    "p": department_prefixes[dept_code],
                }
        
        data_dir = get_path("DATA_DIR")
        departments_path = data_dir / "staged" / "departments.json"
        departments_noprefix_path = data_dir / "staged" / "departmentsNoPrefix.json"
        data_path = data_dir / "staged" / "data.json"
        last_updated_path = data_dir / "staged" / "lastUpdated.json"

        current_time = datetime.now(pytz.timezone(get_setting("TIMEZONE")))
        formatted_time = current_time.strftime("%d.%m.%Y, %H.%M")
        last_updated_info = {
            "t": current_semester[0] + ":" + current_semester[1],
            "u": formatted_time,
        }

        write_json(departments_path, departments_json)
        write_json(departments_noprefix_path, departments_noprefix)
        write_json(data_path, data)
        write_json(last_updated_path, last_updated_info)

        # upload files to s3 possible departmentsOverrides.json

        logger.info("Scraping process completed successfully and files uploaded to S3.")
        return None, None
    except Exception:
        return None, None
