from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import app_constants
from errors import RecoverError
from utils.timing import throttle_before_request, report_success, report_failure


def get_http_session(
    total: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: Optional[tuple[int, ...]] = (429, 500, 502, 503, 504),
    timeout: float = 15.0,
) -> requests.Session:
    """Return a requests Session with retry/backoff and a default timeout via mount.

    Note: Callers should still pass explicit timeouts where appropriate.
    """
    session = requests.Session()
    retry = Retry(
        total=total,
        read=total,
        connect=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    # Set default headers from config (e.g., User-Agent, Accept, etc.)
    try:
        session.headers.update(app_constants.headers)
    except Exception:
        pass
    # Store default timeout on session object for convenience
    session.request = _wrap_with_timeout(session.request, timeout)
    return session


# Centralized request wrappers
def request(
    session: requests.Session,
    method: str,
    url: str,
    *,
    params: Optional[dict] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    ok_status: int = 200,
    tries: int = 5,
    base_delay: float = 1.0,
    name: Optional[str] = None,
    **kwargs,
) -> requests.Response:
    """Make an HTTP request with throttle + bounded retries and classify failures.

    Raises RecoverError after exhausting retries.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(tries):
        try:
            throttle_before_request(base_delay)
            resp = session.request(method, url, params=params, data=data, json=json, **kwargs)
            if resp.status_code == ok_status:
                report_success()
                return resp
            # Handle 4xx hard failures (except 429) without retrying
            if 400 <= resp.status_code < 500 and resp.status_code != 429:
                report_failure()
                raise RecoverError(
                    f"HTTP {resp.status_code} on {name or method}",
                    {"url": url, "status": resp.status_code},
                    code="FETCH_4XX",
                ) from None
            # Else retry (5xx or 429)
            report_failure()
            last_exc = RecoverError(
                f"HTTP {resp.status_code} on {name or method}",
                {"url": url, "status": resp.status_code},
                code="FETCH_RETRY",
            )
        except Exception as e:  # network/timeout or other
            report_failure()
            last_exc = e
            # continue to retry
    # Exhausted retries
    if isinstance(last_exc, RecoverError):
        raise last_exc from None
    raise RecoverError(
        f"Request failed for {name or method}",
        {"url": url, "error": str(last_exc) if last_exc else "unknown"},
        code="FETCH_FAIL",
    ) from None


def get(session: requests.Session, url: str, *, tries: int = 5, base_delay: float = 1.0, name: Optional[str] = None, **kwargs) -> requests.Response:
    return request(session, "GET", url, tries=tries, base_delay=base_delay, name=name, **kwargs)


def post(session: requests.Session, url: str, *, data: Optional[dict] = None, tries: int = 5, base_delay: float = 0.9, name: Optional[str] = None, **kwargs) -> requests.Response:
    return request(session, "POST", url, data=data, tries=tries, base_delay=base_delay, name=name, **kwargs)


def post_oibs(session: requests.Session, data: dict, *, tries: int = 5, base_delay: float = 0.9, name: str = "oibs_post") -> requests.Response:
    return post(session, app_constants.oibs64_url, data=data, tries=tries, base_delay=base_delay, name=name)


def get_catalog(session: requests.Session, dept_code: str, course_code: str, *, tries: int = 5, base_delay: float = 1.0) -> requests.Response:
    url = app_constants.course_catalog_url.replace("{dept_code}", dept_code).replace("{course_code}", course_code)
    return get(session, url, tries=tries, base_delay=base_delay, name="catalog_get")


def _wrap_with_timeout(request_func, timeout: float):
    def wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        return request_func(method, url, **kwargs)

    return wrapped
