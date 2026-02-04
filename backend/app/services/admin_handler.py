"""Admin action dispatcher for /admin endpoint."""

from __future__ import annotations

from typing import Any

from app.api.schemas import AdminResponse
from app.context.service import (
    clear_queue,
    detach_context,
    get_context_snapshot,
    load_context_state,
    publish_context_state,
    reset_failure_count,
    unsuspend_processing,
)
from app.core.constants import AdminAction
from app.core.errors import AppError
from app.services.settings_admin import apply_settings_updates, get_public_settings
from app.storage.s3 import (
    admin_acquire_lock,
    admin_acquire_op_lock,
    admin_op_lock_exists,
    admin_lock_status,
    admin_release_lock,
    admin_release_op_lock,
    admin_validate_lock_token,
)

_MUTATING_ACTIONS: tuple[AdminAction, ...] = (
    AdminAction.CONTEXT_CLEAR_QUEUE,
    AdminAction.CONTEXT_RESET_FAILURES,
    AdminAction.CONTEXT_UNSUSPEND,
    AdminAction.SETTINGS_SET,
)


def handle_admin_action(
    action: AdminAction,
    payload: dict[str, Any] | None,
    lock_token: str | None = None,
) -> tuple[AdminResponse, int]:
    """Execute one admin action and return serialized response and HTTP status."""
    try:
        if action in _MUTATING_ACTIONS:
            if not admin_validate_lock_token(lock_token):
                return _failed(action, "Valid admin lock token is required for mutating actions.", 409)
            if not admin_acquire_op_lock(lock_token):
                return _failed(action, "Another admin operation is in progress.", 409)
            try:
                return _handle_action(action, payload, lock_token=lock_token)
            finally:
                admin_release_op_lock(lock_token)
        return _handle_action(action, payload, lock_token=lock_token)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Admin action failed.",
            "ADMIN_ACTION_FAILED",
            cause=e,
        )
        return _failed(action, err.message, 500)


def _handle_action(
    action: AdminAction,
    payload: dict[str, Any] | None,
    lock_token: str | None,
) -> tuple[AdminResponse, int]:
    """Run concrete admin action logic."""
    if action == AdminAction.ADMIN_LOCK_ACQUIRE:
        result = admin_acquire_lock()
        if result.get("acquired"):
            return _ok(
                action,
                "Admin lock acquired.",
                data={"lock_token": result.get("token"), "lock": result.get("status")},
            )
        return _failed(action, "Admin lock is already active.", 409, data=result.get("status"))

    if action == AdminAction.ADMIN_LOCK_RELEASE:
        if not admin_validate_lock_token(lock_token):
            return _failed(action, "Valid admin lock token is required to release lock.", 409)
        if admin_op_lock_exists():
            return _failed(
                action,
                "Cannot release admin lock while an admin operation is in progress.",
                409,
            )
        if admin_release_lock(lock_token):
            return _ok(action, "Admin lock released.", data=admin_lock_status())
        return _failed(action, "Admin lock release failed.", 409, data=admin_lock_status())

    if action == AdminAction.ADMIN_LOCK_STATUS:
        return _ok(action, "Admin lock status fetched.", data=admin_lock_status())

    if action == AdminAction.CONTEXT_GET:
        try:
            load_context_state(admin=True)
            return _ok(action, "Context fetched.", data={"context": get_context_snapshot(admin=True)})
        finally:
            detach_context(admin=True)

    if action == AdminAction.CONTEXT_CLEAR_QUEUE:
        try:
            load_context_state(admin=True)
            clear_queue(admin=True)
            publish_context_state(admin=True)
            return _ok(action, "Context queue cleared.")
        finally:
            detach_context(admin=True)

    if action == AdminAction.CONTEXT_RESET_FAILURES:
        try:
            load_context_state(admin=True)
            reset_failure_count(admin=True)
            publish_context_state(admin=True)
            return _ok(action, "Context failure count reset.")
        finally:
            detach_context(admin=True)

    if action == AdminAction.CONTEXT_UNSUSPEND:
        try:
            load_context_state(admin=True)
            unsuspend_processing(admin=True)
            publish_context_state(admin=True)
            return _ok(action, "Context unsuspended.")
        finally:
            detach_context(admin=True)

    if action == AdminAction.SETTINGS_GET:
        return _ok(action, "Settings fetched.", data={"settings": get_public_settings()})

    if action == AdminAction.SETTINGS_SET:
        updates: dict[str, Any] = {}
        if isinstance(payload, dict):
            raw_updates = payload.get("updates")
            if isinstance(raw_updates, dict):
                updates = raw_updates

        if not updates:
            return _ok(
                action,
                "No updates provided.",
                data={"results": {}, "applied_count": 0, "failed_count": 0},
            )

        results, applied_count, failed_count = apply_settings_updates(updates)
        data = {
            "results": results,
            "applied_count": applied_count,
            "failed_count": failed_count,
        }
        if failed_count == 0:
            return _ok(action, "All setting updates applied.", data=data)
        if applied_count > 0:
            return _partial(action, "Some setting updates failed.", data=data)
        return _partial(action, "No setting updates were applied.", data=data)

    return _failed(action, "Unsupported admin action.", 400)


def _ok(action: AdminAction, message: str, data: dict[str, Any] | None = None) -> tuple[AdminResponse, int]:
    """Build SUCCESS admin response."""
    return AdminResponse(action=action, status="SUCCESS", message=message, data=data), 200


def _partial(action: AdminAction, message: str, data: dict[str, Any] | None = None) -> tuple[AdminResponse, int]:
    """Build PARTIAL admin response with 207 status."""
    return AdminResponse(action=action, status="PARTIAL", message=message, data=data), 207


def _failed(
    action: AdminAction,
    message: str,
    status_code: int,
    data: dict[str, Any] | None = None,
) -> tuple[AdminResponse, int]:
    """Build FAILED admin response with provided status code."""
    return AdminResponse(action=action, status="FAILED", message=message, data=data), status_code
