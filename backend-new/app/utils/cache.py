import hashlib
import json
from pathlib import Path

from app.core.settings import get_path


def make_key(method, url, params=None, data=None, json_body=None):
    key = {
        "method": method,
        "url": url,
        "params": params,
        "data": data,
        "json": json_body,
    }
    return json.dumps(key, sort_keys=True, default=str)


def hash_content(content):
    if isinstance(content, str):
        content = content.encode("utf-8", errors="replace")
    return hashlib.sha256(content).hexdigest()


class CacheStore:
    def __init__(self, *, parser_version):
        self.parser_version = parser_version
        self._cache = {}
        self._loaded = False

    def load(self):
        self._cache = _load_cache()
        self._loaded = True

    def get(self, cache_key, html_hash):
        if not self._loaded:
            self.load()
        entry = self._cache.get(cache_key)
        if not entry:
            return None
        if entry.get("parser_version") != self.parser_version:
            return None
        if entry.get("hash") != html_hash:
            return None
        return entry.get("parsed")

    def set(self, cache_key, html_hash, parsed):
        if not self._loaded:
            self.load()
        self._cache[cache_key] = {
            "hash": html_hash,
            "parser_version": self.parser_version,
            "parsed": parsed,
        }

    def flush(self):
        if not self._loaded:
            return
        _save_cache(self._cache)


def _cache_dir():
    base = get_path("DATA_DIR")
    path = base / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_path():
    return _cache_dir() / "parsed_cache.json"


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
