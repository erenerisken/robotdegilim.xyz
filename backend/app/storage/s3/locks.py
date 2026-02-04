"""Run/admin lock and admin operation lock management."""

from __future__ import annotations

import time
import uuid
from typing import Any

from app.core.constants import S3_ADMIN_LOCK_FILE, S3_ADMIN_OP_LOCK_FILE, S3_LOCK_FILE
from app.core.errors import AppError

from .common import get_settings
from .state import is_run_lock_held, set_run_lock_held
from .store import delete_object, is_expired, read_json_payload, write_json_payload


def _active_run_lock_data() -> dict[str, Any] | None:
    """Return active run lock payload and cleanup stale lock file."""
    payload = read_json_payload(S3_LOCK_FILE)
    if is_expired(payload):
        delete_object(S3_LOCK_FILE)
        return None
    return payload


def _active_admin_lock_data() -> dict[str, Any] | None:
    """Return active admin lock payload and cleanup stale lock file."""
    payload = read_json_payload(S3_ADMIN_LOCK_FILE)
    if is_expired(payload):
        delete_object(S3_ADMIN_LOCK_FILE)
        return None
    return payload


def _active_admin_op_lock_data() -> dict[str, Any] | None:
    """Return active admin op-lock payload if it matches active admin lock token."""
    op_payload = read_json_payload(S3_ADMIN_OP_LOCK_FILE)
    if is_expired(op_payload):
        delete_object(S3_ADMIN_OP_LOCK_FILE)
        return None

    admin_payload = _active_admin_lock_data()
    if not admin_payload:
        delete_object(S3_ADMIN_OP_LOCK_FILE)
        return None

    if op_payload.get("holder_token") != admin_payload.get("token"):
        delete_object(S3_ADMIN_OP_LOCK_FILE)
        return None
    return op_payload


def admin_lock_exists() -> bool:
    """Return whether admin lock is currently active."""
    return _active_admin_lock_data() is not None


def run_lock_exists() -> bool:
    """Return whether run lock is currently active."""
    return _active_run_lock_data() is not None


def admin_op_lock_exists() -> bool:
    """Return whether admin operation lock is currently active and valid."""
    return _active_admin_op_lock_data() is not None


def acquire_lock() -> bool:
    """Acquire run lock for this instance if available and admin lock is not active."""
    try:
        if admin_lock_exists():
            return False
        if is_run_lock_held():
            return True

        now = time.time()
        settings = get_settings()
        current_payload = _active_run_lock_data()
        if current_payload:
            return False

        payload = {
            "owner": settings.S3_LOCK_OWNER_ID,
            "acquired_at": now,
            "expires_at": now + float(settings.S3_LOCK_TIMEOUT_SECONDS),
        }
        write_json_payload(S3_LOCK_FILE, payload)
        set_run_lock_held(True)
        return True
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError("Failed to acquire run lock.", "LOCK_ACQUIRE_FAILED", cause=e)


def release_lock() -> bool:
    """Release run lock when current lock owner matches this instance."""
    try:
        if not is_run_lock_held():
            return True

        payload = read_json_payload(S3_LOCK_FILE)
        owner_id = get_settings().S3_LOCK_OWNER_ID
        if not payload or payload.get("owner") != owner_id:
            set_run_lock_held(False)
            return False

        delete_object(S3_LOCK_FILE)
        set_run_lock_held(False)
        return True
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError("Failed to release run lock.", "LOCK_RELEASE_FAILED", cause=e)


def admin_acquire_lock() -> dict[str, Any]:
    """Acquire admin lock and return acquisition status with lock metadata."""
    try:
        now = time.time()
        current_payload = read_json_payload(S3_ADMIN_LOCK_FILE)
        if current_payload and not is_expired(current_payload, now=now):
            return {"acquired": False, "status": admin_lock_status()}

        token = str(uuid.uuid4())
        settings = get_settings()
        payload = {
            "owner": settings.S3_LOCK_OWNER_ID,
            "token": token,
            "acquired_at": now,
            "expires_at": now + float(settings.ADMIN_LOCK_TIMEOUT_SECONDS),
        }
        write_json_payload(S3_ADMIN_LOCK_FILE, payload)
        return {"acquired": True, "token": token, "status": admin_lock_status()}
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to acquire admin lock.",
            "ADMIN_LOCK_ACQUIRE_FAILED",
            cause=e,
        )


def admin_validate_lock_token(token: str | None) -> bool:
    """Return True when token matches active admin lock token."""
    if not token:
        return False
    lock_payload = _active_admin_lock_data()
    if not lock_payload:
        return False
    return lock_payload.get("token") == token


def admin_release_lock(token: str | None) -> bool:
    """Release admin lock when token is valid and no admin operation is running."""
    try:
        if not admin_validate_lock_token(token):
            return False
        if admin_op_lock_exists():
            return False

        delete_object(S3_ADMIN_LOCK_FILE)
        delete_object(S3_ADMIN_OP_LOCK_FILE)
        return True
    except Exception as e:
        raise e if isinstance(e, AppError) else AppError(
            "Failed to release admin lock.",
            "ADMIN_LOCK_RELEASE_FAILED",
            cause=e,
        )


def admin_lock_status() -> dict[str, Any]:
    """Return admin lock status metadata without exposing lock token."""
    lock_payload = _active_admin_lock_data()
    if not lock_payload:
        return {"active": False}
    return {
        "active": True,
        "owner": lock_payload.get("owner"),
        "acquired_at": lock_payload.get("acquired_at"),
        "expires_at": lock_payload.get("expires_at"),
    }


def admin_acquire_op_lock(token: str | None) -> bool:
    """Acquire admin operation lock for validated admin token."""
    if not admin_validate_lock_token(token):
        return False
    if admin_op_lock_exists():
        return False

    now = time.time()
    expires_in = float(get_settings().ADMIN_LOCK_TIMEOUT_SECONDS)
    payload = {
        "holder_token": token,
        "acquired_at": now,
        "expires_at": now + expires_in,
    }
    write_json_payload(S3_ADMIN_OP_LOCK_FILE, payload)
    return True


def admin_release_op_lock(token: str | None) -> bool:
    """Release admin operation lock when holder token matches."""
    payload = read_json_payload(S3_ADMIN_OP_LOCK_FILE)
    if not payload:
        return True
    if payload.get("holder_token") != token:
        return False
    delete_object(S3_ADMIN_OP_LOCK_FILE)
    return True
