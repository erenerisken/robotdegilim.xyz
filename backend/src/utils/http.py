from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.config import app_constants
from src.errors import RecoverError
from src.utils.timing import throttle_before_request, report_success, report_failure


_HTTP_SESSION: Optional[requests.Session] = None


def get_http_session(
    total: int = app_constants.global_retries,
    backoff_factor: float = 0.5,
    status_forcelist: Optional[tuple[int, ...]] = (429, 500, 502, 503, 504),
    *,
    refresh: bool = False,
) -> requests.Session:
    """Return a cached requests Session with retry/backoff configured.

    Pass refresh=True to rebuild the session (e.g., if headers or retry policy
    must change during runtime). Subsequent calls return the same instance for
    connection pooling efficiency.
    """
    global _HTTP_SESSION
    if _HTTP_SESSION is not None and not refresh:
        return _HTTP_SESSION
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
    try:
        session.headers.update(app_constants.headers)
    except Exception:
        pass
    _HTTP_SESSION = session
    return session


def reset_http_session():
    """Clear cached HTTP session (tests or dynamic policy reload)."""
    global _HTTP_SESSION
    _HTTP_SESSION = None


# Centralized request wrappers
def request(
    method: str,
    url: str,
    *,
    params: Optional[dict] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    ok_status: int = 200,
    tries: int = app_constants.global_retries,
    base_delay: float = 1.0,
    name: Optional[str] = None,
    **kwargs,
) -> requests.Response:
    """Make an HTTP request with throttle + bounded retries and classify failures.

    Raises RecoverError after exhausting retries.
    """
    last_exc: Optional[Exception] = None
    session = get_http_session()
    for attempt in range(tries):
        try:
            throttle_before_request(base_delay)
            if "timeout" not in kwargs:
                kwargs["timeout"] = app_constants.http_timeout
            resp = session.request(method, url, params=params, data=data, json=json, **kwargs)
            if resp.status_code == ok_status:
                report_success()
                return resp
            # Handle 4xx hard failures (except 429) without retrying
            if 400 <= resp.status_code < 500 and resp.status_code != 429:
                report_failure()
                raise RecoverError(
                    f"HTTP {resp.status_code} on {name or method}: url: {url}, status: {resp.status_code}, code=FETCH_4XX"
                )
            # Else retry (5xx or 429)
            report_failure()
            last_exc = RecoverError(
                f"HTTP {resp.status_code} on {name or method}: url: {url}, status: {resp.status_code}, code=FETCH_RETRY"
            )
        except Exception as e:  # network/timeout or other
            report_failure()
            last_exc = e
            # continue to retry
    # Exhausted retries
    if isinstance(last_exc, RecoverError):
        raise last_exc
    raise RecoverError(
        f"Request failed for {name or method}: url: {url}, error: {str(last_exc) if last_exc else 'unknown'}, code=FETCH_FAIL"
    )


def get(
    url: str,
    *,
    tries: int = app_constants.global_retries,
    base_delay: float = 1.0,
    name: Optional[str] = None,
    **kwargs,
) -> requests.Response:
    return request("GET", url, tries=tries, base_delay=base_delay, name=name, **kwargs)


def post(
    url: str,
    *,
    data: Optional[dict] = None,
    tries: int = app_constants.global_retries,
    base_delay: float = 0.9,
    name: Optional[str] = None,
    **kwargs,
) -> requests.Response:
    return request(
        "POST", url, data=data, tries=tries, base_delay=base_delay, name=name, **kwargs
    )
