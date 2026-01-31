from app.utils.http import get, post
from app.core.settings import get_setting
from app.core.errors import ScrapeError
from app.utils.cache import make_key, hash_content

def get_main_page():
    try:
        response = get(get_setting("OIBS64_URL"), name="scrape_get_main_page")
        response.encoding = "utf-8"
        cache_key= make_key("GET", get_setting("OIBS64_URL"))
        html_hash= hash_content(response.text)
        return cache_key, html_hash, response
    except Exception as e:
        raise ScrapeError(
            message="Failed to get main page",
            code="SCRAPE_MAIN_PAGE_FAILED",
            context={"url": get_setting("OIBS64_URL")},
            cause=e,
        )
