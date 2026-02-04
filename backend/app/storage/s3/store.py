"""Shared object and JSON payload access across real/mock backends."""

from __future__ import annotations

import json
import time
from typing import Any

from app.storage.local import read_json as read_local_json
from app.storage.local import write_json as write_local_json

from .common import _is_real_s3_enabled, _mock_path
from .mock_backend import (
    delete_object as delete_object_mock,
    object_exists as object_exists_mock,
    read_object_bytes as read_object_bytes_mock,
    write_object_bytes as write_object_bytes_mock,
)
from .real_backend import (
    delete_object as delete_object_real,
    object_exists as object_exists_real,
    read_object_bytes as read_object_bytes_real,
    write_object_bytes as write_object_bytes_real,
)


def read_object_bytes(key: str) -> bytes | None:
    """Read object bytes from configured backend."""
    return read_object_bytes_real(key) if _is_real_s3_enabled() else read_object_bytes_mock(key)


def write_object_bytes(key: str, content: bytes) -> None:
    """Write object bytes to configured backend."""
    if _is_real_s3_enabled():
        write_object_bytes_real(key, content)
    else:
        write_object_bytes_mock(key, content)


def object_exists(key: str) -> bool:
    """Check object existence in configured backend."""
    return object_exists_real(key) if _is_real_s3_enabled() else object_exists_mock(key)


def delete_object(key: str) -> bool:
    """Delete object from configured backend."""
    return delete_object_real(key) if _is_real_s3_enabled() else delete_object_mock(key)


def read_json_payload(key: str) -> dict[str, Any] | None:
    """Read JSON payload from storage key and normalize invalid payloads as None."""
    if _is_real_s3_enabled():
        raw = read_object_bytes_real(key)
        if raw is None:
            return None
        try:
            payload = json.loads(raw.decode("utf-8"))
            return payload if isinstance(payload, dict) and payload else None
        except Exception:
            return None

    payload = read_local_json(_mock_path(key))
    return payload if payload else None


def write_json_payload(key: str, payload: dict[str, Any]) -> None:
    """Write JSON payload to storage key."""
    if _is_real_s3_enabled():
        write_object_bytes_real(key, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        return
    write_local_json(_mock_path(key), payload)


def is_expired(payload: dict[str, Any] | None, *, now: float | None = None) -> bool:
    """Return True when payload is missing or its expires_at is in the past."""
    if not payload:
        return True
    current = time.time() if now is None else now
    try:
        return float(payload.get("expires_at", 0.0)) <= current
    except Exception:
        return True
