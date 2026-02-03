"""HTTP helper functions with retry/backoff and shared session management."""

from collections.abc import Iterable
import random
import time
from typing import Any

import requests
from requests import Response, Session

from app.core.errors import AppError
from app.core.settings import get_settings

_SESSION: Session | None = None


def get_session() -> Session:
    """Return a shared requests session configured with default headers."""
    global _SESSION
    if _SESSION is not None:
        return _SESSION
    session = requests.Session()
    settings = get_settings()
    headers = settings.DEFAULT_HEADERS
    if isinstance(headers, dict):
        session.headers.update(headers)
    _SESSION = session
    return _SESSION


def reset_session() -> None:
    """Reset the shared HTTP session."""
    global _SESSION
    _SESSION = None


def request(
    method: str,
    url: str,
    *,
    params: Any = None,
    data: Any = None,
    json_body: Any = None,
    ok_status: Iterable[int] | None = None,
    name: str | None = None,
) -> Response:
    """Send an HTTP request with retries and backoff."""
    settings = get_settings()
    timeout = float(settings.HTTP_TIMEOUT)
    max_tries = int(settings.GLOBAL_RETRIES)
    base_delay = float(settings.RETRY_BASE_DELAY)
    jitter = float(settings.RETRY_JITTER)

    ctx: dict[str, Any] = {"method": method, "url": url}
    if params:
        ctx["params"] = params
    if data:
        ctx["data"] = data
    if json_body:
        ctx["json"] = json_body
    if name:
        ctx["name"] = name

    if ok_status is None:
        ok_status = {200}
    else:
        ok_status = set(ok_status)
    last_error: Exception | None = None
    for attempt in range(1, max_tries + 1):
        _maybe_throttle()
        try:
            resp = get_session().request(
                method,
                url,
                params=params,
                data=data,
                json=json_body,
                timeout=timeout,
            )
        except Exception as e:
            last_error = e
            _sleep_with_jitter(base_delay, jitter, attempt)
            continue

        if resp.status_code in ok_status:
            return resp

        if _should_retry(resp.status_code):
            ctx["status_code"] = resp.status_code
            last_error = AppError("HTTP request failed, retrying", "HTTP_REQUEST_FAILED", context=ctx)
            _sleep_with_jitter(base_delay, jitter, attempt)
            continue

        ctx["status_code"] = resp.status_code
        raise AppError("HTTP request failed, no need to retry", "HTTP_REQUEST_FAILED", context=ctx)

    raise AppError("HTTP request failed, giving up", "HTTP_REQUEST_FAILED", context=ctx, cause=last_error)


def get(url: str, **kwargs: Any) -> Response:
    """Send an HTTP GET request."""
    try:
        return request("GET", url, **kwargs)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("GET request failed", "GET_REQUEST_FAILED", context={"url": url, **kwargs}, cause=e)
        raise err


def post(url: str, *, data: Any = None, **kwargs: Any) -> Response:
    """Send an HTTP POST request."""
    try:
        return request("POST", url, data=data, **kwargs)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("POST request failed", "POST_REQUEST_FAILED", context={"url": url, "data": data, **kwargs}, cause=e)
        raise err


def _should_retry(status_code: int | None) -> bool:
    """Return True if the response status should be retried."""
    if status_code is None:
        return True
    if status_code == 429:
        return True
    if 500 <= status_code <= 599:
        return True
    return False


def _sleep_with_jitter(base_delay: float, jitter: float, attempt: int) -> None:
    """Sleep with linear backoff and random jitter."""
    delay = (base_delay * attempt) + random.uniform(0, jitter)
    time.sleep(max(0.0, delay))


def _maybe_throttle() -> None:
    """Apply throttling when enabled (placeholder)."""
    try:
        throttle = get_settings().THROTTLE_ENABLED
        if throttle:
            # throttle will be implemented later
            pass
    except Exception:
        pass
