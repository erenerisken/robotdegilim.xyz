from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from src.config import app_constants
from src.errors import NetworkError
from src.utils.timing import throttle_before_request, report_success, report_failure


_HTTP_SESSION: Optional[requests.Session] = None


def get_http_session(
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
    adapter = HTTPAdapter()
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
    name: Optional[str] = None,
    **kwargs,
) -> requests.Response:
    """Make an HTTP request with throttle + bounded retries and classify failures.

    Raises RecoverError after exhausting retries.
    """
    last_exc: Optional[Exception] = None
    max_tries = app_constants.global_retries
    session = get_http_session()
    for attempt in range(max_tries):
        try:
            throttle_before_request()
            resp = session.request(method, url, params=params, data=data, json=json, timeout=app_constants.http_timeout, **kwargs)
            if resp.status_code == ok_status:
                report_success()
                return resp
            # Handle 4xx hard failures (except 429) without retrying
            if 400 <= resp.status_code < 500 and resp.status_code != 429:
                report_failure()
                raise NetworkError(
                    f"HTTP {resp.status_code} on {name or method}: url: {url}, status: {resp.status_code}, code=FETCH_4XX"
                )
            # Else retry (5xx or 429)
            report_failure()
            last_exc = NetworkError(
                f"HTTP {resp.status_code} on {name or method}: url: {url}, status: {resp.status_code}, code=FETCH_RETRY"
            )
        except Exception as e:  # network/timeout or other
            report_failure()
            last_exc = e
            # continue to retry
    # Exhausted retries
    if isinstance(last_exc, NetworkError):
        raise last_exc
    raise NetworkError(
        f"Request failed for {name or method}: url: {url}, error: {str(last_exc) if last_exc else 'unknown'}, code=FETCH_FAIL"
    )


def get(
    url: str,
    *,
    name: Optional[str] = None,
    **kwargs,
) -> requests.Response:
    try:
        return request("GET", url, name=name, **kwargs)
    except Exception as e:
        raise NetworkError(f"GET request failed for {name or url}, error: {str(e)}") from e

def post(
    url: str,
    *,
    data: Optional[dict] = None,
    name: Optional[str] = None,
    **kwargs,
) -> requests.Response:
    try:
        return request(
            "POST", url, data=data, name=name, **kwargs
        )
    except Exception as e:
        raise NetworkError(f"POST request failed for {name or url}, error: {str(e)}") from e
