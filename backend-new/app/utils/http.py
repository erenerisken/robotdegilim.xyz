import random
import time
import requests

from app.core.errors import AppError
from app.core.settings import get_settings

_SESSION = None

def get_session():
    global _SESSION
    if _SESSION is not None:
        return _SESSION
    session = requests.Session()
    settings= get_settings()
    headers = settings.DEFAULT_HEADERS
    if isinstance(headers, dict):
        session.headers.update(headers)
    _SESSION = session
    return _SESSION

def reset_session():
    global _SESSION
    _SESSION = None

def request(method, url, *, params=None, data=None, json_body=None, ok_status=None, name=None):
    settings = get_settings()
    timeout = float(settings.HTTP_TIMEOUT)
    max_tries = int(settings.GLOBAL_RETRIES)
    base_delay = float(settings.RETRY_BASE_DELAY)
    jitter = float(settings.RETRY_JITTER)

    ctx={"method": method, "url": url}
    if params:
        ctx["params"] = params
    if data:
        ctx["data"] = data
    if json_body:
        ctx["json"] = json_body
    if name:
        ctx["name"] = name

    if ok_status is None:
        ok_status = [200]
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


def get(url, **kwargs):
    try:
        return request("GET", url, **kwargs)
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("GET request failed", "GET_REQUEST_FAILED", context={"url": url,**kwargs}, cause=e)
        raise err


def post(url, *, data=None, **kwargs):
    try:
        return request("POST", url, data=data, **kwargs)
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("POST request failed", "POST_REQUEST_FAILED", context={"url": url, "data": data, **kwargs}, cause=e)
        raise err


def _should_retry(status_code):
    if status_code is None:
        return True
    if status_code == 429:
        return True
    if 500 <= status_code <= 599:
        return True
    return False


def _sleep_with_jitter(base_delay, jitter, attempt):
    delay = (base_delay * attempt) + random.uniform(0, jitter)
    time.sleep(max(0.0, delay))


def _maybe_throttle():
    try:
        throttle=get_settings().THROTTLE_ENABLED
        if throttle:
            # throttle will be implemented later
            pass
    except Exception:
        pass
