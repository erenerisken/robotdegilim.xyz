"""Low-level HTTP client for backend /admin endpoint."""

from __future__ import annotations

import json
import ssl
from typing import Any
from urllib import error, request

from .config import ADMIN_SECRET, BASE_URL, TIMEOUT_SECONDS, VERIFY_TLS


def _parse_json_bytes(raw: bytes) -> dict[str, Any]:
    """Parse JSON body into dict or raise clear runtime error."""
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise RuntimeError("Admin endpoint returned non-JSON response.") from e
    if not isinstance(payload, dict):
        raise RuntimeError("Admin endpoint JSON response is not an object.")
    return payload


def admin_post(action: str, payload: dict[str, Any] | None = None, lock_token: str | None = None) -> tuple[int, dict[str, Any]]:
    """Send one /admin action request and return `(status_code, response_json)`."""
    if not ADMIN_SECRET:
        raise RuntimeError("ADMIN_SECRET is empty in scripts/admin/config.py")

    body: dict[str, Any] = {"action": action}
    if payload is not None:
        body["payload"] = payload

    headers = {
        "Content-Type": "application/json",
        "X-Admin-Secret": ADMIN_SECRET,
    }
    if lock_token:
        headers["X-Admin-Lock-Token"] = lock_token

    url = f"{BASE_URL.rstrip('/')}/admin"
    req = request.Request(
        url=url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    context = None
    if url.lower().startswith("https://") and not VERIFY_TLS:
        context = ssl._create_unverified_context()  # noqa: SLF001

    try:
        with request.urlopen(req, timeout=TIMEOUT_SECONDS, context=context) as resp:
            return resp.status, _parse_json_bytes(resp.read())
    except error.HTTPError as e:
        raw = e.read()
        return e.code, _parse_json_bytes(raw)
    except error.URLError as e:
        raise RuntimeError(f"Cannot reach admin endpoint at {url}: {e.reason}") from e
