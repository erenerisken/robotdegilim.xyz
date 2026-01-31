from app.utils.http import get, post
from app.core.logging import get_logger
from app.core.errors import ScrapeError
from app.utils.cache import make_key, hash_content
from app.core.constants import OIBS64_URL, COURSE_CATALOG_URL

def get_main_page():
    try:
        response = get(OIBS64_URL, name="scrape_get_main_page")
        response.encoding = "utf-8"
        cache_key= make_key("GET", OIBS64_URL)
        html_hash= hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        raise ScrapeError(
            message="Failed to get main page",
            code="SCRAPE_MAIN_PAGE_FAILED",
            context={"url": OIBS64_URL},
            cause=e,
        )

def get_department_page(dept_code,semester_code):
    data = {
        "textWithoutThesis": 1,
        "select_dept": dept_code,
        "select_semester": semester_code,
        "submit_CourseList": "Submit",
        "hidden_redir": "Login",
    }
    try:
        response = post(OIBS64_URL, data=data, name="scrape_get_department_page")
        response.encoding = "utf-8"
        cache_key= make_key("POST", OIBS64_URL, data=data)
        html_hash= hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        raise ScrapeError(
            message=f"Failed to get department page",
            code="SCRAPE_DEPT_PAGE_FAILED",
            context={"dept_code": dept_code, "semester_code": semester_code},
            cause=e,
        )
    
def get_course_page(course_code):
    data = {
        "SubmitCourseInfo": "Course Info",
        "text_course_code": course_code,
        "hidden_redir": "Course_List",
    }
    try:
        response = post(OIBS64_URL, data=data, name="scrape_get_course_page")
        response.encoding = "utf-8"
        cache_key= make_key("POST", OIBS64_URL, data=data)
        html_hash= hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        raise ScrapeError(
            message=f"Failed to get course page",
            code="SCRAPE_COURSE_PAGE_FAILED",
            context={"course_code": course_code},
            cause=e,
        )
    
def get_section_page(section_code) :
    data = {"submit_section": section_code, "hidden_redir": "Course_Info"}
    try:
        response = post(OIBS64_URL, data=data, name="scrape_get_section_page")
        response.encoding = "utf-8"
        cache_key= make_key("POST", OIBS64_URL, data=data)
        html_hash= hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        raise ScrapeError(
            message=f"Failed to get section page",
            code="SCRAPE_SECTION_PAGE_FAILED",
            context={"section_code": section_code},
            cause=e,
            )
    
def get_course_catalog_page(dept_code: str, course_code: str):
    try:
        url = COURSE_CATALOG_URL.replace("{dept_code}", dept_code).replace("{course_code}", course_code)
        response = get(url, name="scrape_get_course_catalog_page")
        response.encoding = "utf-8"
        cache_key= make_key("GET", url)
        html_hash= hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        err= ScrapeError(
            message=f"Failed to get course catalog page",
            code="SCRAPE_COURSE_CATALOG_PAGE_FAILED",
            context={"dept_code": dept_code, "course_code": course_code},
            cause=e,
        )
        logger = get_logger("scrape")
        logger.warning(err.to_log())
        return None, None, None
