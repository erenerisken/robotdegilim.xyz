"""Utilities for cache-key generation, content hashing, and parsed-cache storage."""

import hashlib
import json
from pathlib import Path
from typing import Any

from app.core.errors import AppError


def make_key(method: str, url: str, params: Any = None, data: Any = None, json_body: Any = None) -> str:
    """Build a stable cache key from request components."""
    key = {
        "method": method,
        "url": url,
        "params": params,
        "data": data,
        "json": json_body,
    }
    return json.dumps(key, sort_keys=True, default=str)


def hash_content(content: str | bytes | bytearray | memoryview) -> str:
    """Return SHA-256 hash of content as a hex string."""
    if content is None:
        raise AppError("Content to hash must not be None", "HASH_CONTENT_FAILED")
    if isinstance(content, str):
        content = content.encode("utf-8", errors="replace")
    elif isinstance(content, (bytes, bytearray, memoryview)):
        content = bytes(content)
    else:
        raise AppError("Content to hash must be str or bytes-like", "HASH_CONTENT_FAILED")
    return hashlib.sha256(content).hexdigest()


class CacheStore:
    """Simple lazy-loaded parsed cache backed by a JSON file."""

    def __init__(self, *, path: Path, parser_version: str):
        self.path = path
        self.parser_version = parser_version
        self._cache: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def load(self) -> None:
        """Load cache from disk once."""
        self._cache = _load_cache(self.path)
        self._loaded = True

    def get(self, cache_key: str, html_hash: str) -> Any | None:
        """Return cached parsed payload if parser version and hash match."""
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

    def set(self, cache_key: str, html_hash: str, parsed: Any) -> None:
        """Set or replace a cache entry."""
        if not self._loaded:
            self.load()
        self._cache[cache_key] = {
            "hash": html_hash,
            "parser_version": self.parser_version,
            "parsed": parsed,
        }

    def flush(self) -> None:
        """Persist in-memory cache to disk."""
        if not self._loaded:
            return
        _save_cache(self._cache, self.path)


def _load_cache(path: Path) -> dict[str, dict[str, Any]]:
    """Load cache file; return an empty dict if missing or invalid."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_cache(cache: dict[str, dict[str, Any]], path: Path) -> None:
    """Write cache JSON to disk."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=4), encoding="utf-8")
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to save cache", "SAVE_CACHE_FAILED", context={"path": str(path)}, cause=e)
        raise err
