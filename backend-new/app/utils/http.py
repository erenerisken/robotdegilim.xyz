import random
import time

import requests

from app.core.errors import NetworkError
from app.core.settings import get_setting

_SESSION = None


def get_session():
    global _SESSION
    if _SESSION is not None:
        return _SESSION
    session = requests.Session()
    headers = get_setting("DEFAULT_HEADERS", {})
    if isinstance(headers, dict):
        session.headers.update(headers)
    _SESSION = session
    return _SESSION


def reset_session():
    global _SESSION
    _SESSION = None


def request(method, url, *, params=None, data=None, json_body=None, ok_status=200, name=None):
    timeout = float(get_setting("HTTP_TIMEOUT", 15))
    max_tries = int(get_setting("GLOBAL_RETRIES", 5))
    base_delay = float(get_setting("RETRY_BASE_DELAY", 1.0))
    jitter = float(get_setting("RETRY_JITTER", 0.25))

    last_error = None
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

        if resp.status_code == ok_status:
            return resp

        if _should_retry(resp.status_code):
            last_error = NetworkError(_format_error(method, url, name, resp.status_code))
            _sleep_with_jitter(base_delay, jitter, attempt)
            continue

        raise NetworkError(_format_error(method, url, name, resp.status_code))

    raise NetworkError(
        _format_error(
            method,
            url,
            name,
            None,
            extra=str(last_error) if last_error else "unknown error",
        )
    )


def get(url, **kwargs):
    return request("GET", url, **kwargs)


def post(url, *, data=None, **kwargs):
    return request("POST", url, data=data, **kwargs)


def _should_retry(status_code):
    if status_code is None:
        return True
    if status_code == 429:
        return True
    if 500 <= status_code <= 599:
        return True
    return False


def _format_error(method, url, name, status, *, extra=None):
    label = name or f"{method} {url}"
    if status is None:
        return f"Request failed for {label}: {extra}"
    return f"HTTP {status} for {label}"


def _sleep_with_jitter(base_delay, jitter, attempt):
    delay = (base_delay * attempt) + random.uniform(0, jitter)
    time.sleep(max(0.0, delay))


def _maybe_throttle():
    try:
        throttle=get_setting("THROTTLE_ENABLED", False)
        if throttle:
            # throttle will be implemented later
            pass
    except Exception:
        pass
