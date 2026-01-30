import base64
import json
import random
import time
from pathlib import Path

import requests

from app.core.errors import NetworkError
from app.core.settings import get_setting

_SESSION = None


class CachedResponse:
    def __init__(self, status_code, content, headers, from_cache):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}
        self.from_cache = from_cache

    @property
    def text(self):
        try:
            return self.content.decode("utf-8", errors="replace")
        except Exception:
            return ""


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

    cache_key = _cache_key(method, url, params, data, json_body)
    cache_entry = _load_cache_entry(cache_key)
    headers = _conditional_headers(cache_entry)

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
                headers=headers,
                timeout=timeout,
            )
        except Exception as e:
            last_error = e
            _sleep_with_jitter(base_delay, jitter, attempt)
            continue

        if resp.status_code == 304:
            cached = _cached_response(cache_entry)
            if cached is not None:
                return cached
            return resp

        if resp.status_code == ok_status:
            _save_cache_entry(cache_key, resp)
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


def _cache_dir():
    base = Path(get_setting("DATA_DIR", "data"))
    path = base / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_path():
    return _cache_dir() / "http_cache.json"


def _load_cache():
    path = _cache_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache):
    path = _cache_path()
    path.write_text(json.dumps(cache), encoding="utf-8")


def _cache_key(method, url, params, data, json_body):
    key = {
        "method": method,
        "url": url,
        "params": params,
        "data": data,
        "json": json_body,
    }
    return json.dumps(key, sort_keys=True, default=str)


def _load_cache_entry(cache_key):
    cache = _load_cache()
    return cache.get(cache_key)


def _save_cache_entry(cache_key, resp):
    etag = resp.headers.get("ETag")
    last_modified = resp.headers.get("Last-Modified")
    if not etag and not last_modified:
        return
    body_b64 = base64.b64encode(resp.content).decode("ascii")
    cache = _load_cache()
    cache[cache_key] = {
        "etag": etag,
        "last_modified": last_modified,
        "status_code": resp.status_code,
        "headers": dict(resp.headers),
        "body_b64": body_b64,
    }
    _save_cache(cache)


def _conditional_headers(cache_entry):
    if not cache_entry:
        return None
    headers = {}
    if cache_entry.get("etag"):
        headers["If-None-Match"] = cache_entry["etag"]
    if cache_entry.get("last_modified"):
        headers["If-Modified-Since"] = cache_entry["last_modified"]
    return headers or None


def _cached_response(cache_entry):
    if not cache_entry:
        return None
    try:
        body = base64.b64decode(cache_entry.get("body_b64", ""))
    except Exception:
        body = b""
    return CachedResponse(
        status_code=int(cache_entry.get("status_code", 200)),
        content=body,
        headers=cache_entry.get("headers", {}),
        from_cache=True,
    )
