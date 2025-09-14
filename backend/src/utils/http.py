from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import app_constants


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


def _wrap_with_timeout(request_func, timeout: float):
    def wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        return request_func(method, url, **kwargs)

    return wrapped
