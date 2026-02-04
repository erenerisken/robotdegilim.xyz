"""Context state service for loading, mutating, and publishing app context."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.context.schema import AppContext
from app.core.constants import CONTEXT_KEY, LOGGER_APP, RequestType
from app.core.errors import AppError
from app.core.logging import log_item
from app.core.paths import downloaded_path, published_path, staged_path
from app.core.settings import get_settings
from app.storage.local import move_file, read_json, write_json
from app.storage.s3 import download_file, s3_file_exists, upload_file


@dataclass
class _ContextStore:
    """Internal in-memory context storage per operation class."""

    original: AppContext | None = None
    working: AppContext | None = None
    loaded: bool = False


_RUN_STORE = _ContextStore()
_ADMIN_STORE = _ContextStore()


def _store(admin: bool) -> _ContextStore:
    """Return run or admin context store."""
    return _ADMIN_STORE if admin else _RUN_STORE


def load_context_state(*, admin: bool = False) -> None:
    """Load context from storage once and keep original/working snapshots."""
    store = _store(admin)
    try:
        if store.loaded:
            return
        if s3_file_exists(CONTEXT_KEY):
            local_path = downloaded_path(CONTEXT_KEY)
            download_file(CONTEXT_KEY, local_path)
            data = read_json(local_path)
            store.original = AppContext(**data)
            store.working = store.original.model_copy(deep=True)
        else:
            store.original = AppContext()
            store.working = store.original.model_copy(deep=True)
        store.loaded = True
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to load context",
            "CONTEXT_LOAD_FAILED",
            cause=e,
        )
        raise err


def publish_context_state(*, admin: bool = False) -> None:
    """Persist current context copy and publish it locally and in S3."""
    store = _store(admin)
    try:
        if not store.loaded or store.working is None:
            return
        store.original = store.working.model_copy(deep=True)
        local_staged_path = staged_path(CONTEXT_KEY)
        write_json(local_staged_path, store.original.model_dump())
        upload_file(local_staged_path, CONTEXT_KEY, _admin=admin)
        move_file(local_staged_path, published_path(CONTEXT_KEY))
        detach_context(admin=admin)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to publish context",
            "CONTEXT_PUBLISH_FAILED",
            cause=e,
        )
        raise err


def detach_context(*, admin: bool = False) -> None:
    """Clear the selected in-memory context state."""
    store = _store(admin)
    store.original = None
    store.working = None
    store.loaded = False


def _ensure_context_loaded(*, admin: bool = False) -> _ContextStore:
    """Ensure selected context store is loaded and valid."""
    store = _store(admin)
    if not store.loaded:
        load_context_state(admin=admin)
    if store.original is None or store.working is None:
        raise AppError("Context is not loaded", "CONTEXT_NOT_LOADED")
    return store


def _ensure_not_suspended(*, admin: bool = False) -> None:
    """Raise when selected context is suspended."""
    store = _ensure_context_loaded(admin=admin)
    if store.working is not None and store.working.suspended:
        raise AppError("AppContext is suspended", "CONTEXT_SUSPENDED")


def get_context_snapshot(*, admin: bool = False) -> dict[str, object]:
    """Return current in-memory context snapshot for selected store."""
    store = _ensure_context_loaded(admin=admin)
    return store.working.model_dump() if store.working is not None else AppContext().model_dump()


def enqueue_request(request_type: RequestType, *, admin: bool = False) -> bool:
    """Queue request type if supported and not already queued."""
    try:
        store = _ensure_context_loaded(admin=admin)
        _ensure_not_suspended(admin=admin)
        return store.working.enqueue(request_type)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to queue request",
            "REQUEST_QUEUE_FAILED",
            cause=e,
        )
        raise err


def resolve_request(request_type: RequestType, *, admin: bool = False) -> tuple[bool, RequestType]:
    """Return next queued request or incoming request when queue is empty."""
    try:
        store = _ensure_context_loaded(admin=admin)
        _ensure_not_suspended(admin=admin)
        next_request = store.working.dequeue()
        if next_request is None:
            return False, request_type
        return True, next_request
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to get next request",
            "REQUEST_GET_FAILED",
            cause=e,
        )
        raise err


def record_failure(*, admin: bool = False) -> None:
    """Increment error count and suspend context at configured threshold."""
    try:
        store = _ensure_context_loaded(admin=admin)
        _ensure_not_suspended(admin=admin)
        if store.working.mark_failure(get_settings().CONTEXT_MAX_ERRORS):
            log_item(
                LOGGER_APP,
                logging.WARNING,
                AppError(
                    "AppContext has been suspended due to exceeding maximum error count",
                    "CONTEXT_SUSPENDED",
                ),
            )
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to increment error count",
            "ERROR_INCREMENT_FAILED",
            cause=e,
        )
        raise err


def record_success(*, admin: bool = False) -> None:
    """Decrement error count after successful processing."""
    try:
        store = _ensure_context_loaded(admin=admin)
        _ensure_not_suspended(admin=admin)
        store.working.mark_success()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to decrement error count",
            "ERROR_DECREMENT_FAILED",
            cause=e,
        )
        raise err


def clear_queue(*, admin: bool = False) -> None:
    """Clear queued requests in selected context store."""
    try:
        store = _ensure_context_loaded(admin=admin)
        if not admin:
            _ensure_not_suspended(admin=admin)
        store.working.clear_queue()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to clear request queue",
            "QUEUE_CLEAR_FAILED",
            cause=e,
        )
        raise err


def unsuspend_processing(*, admin: bool = False) -> None:
    """Unsuspend selected context store."""
    try:
        store = _ensure_context_loaded(admin=admin)
        store.working.unsuspend()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to unsuspend context",
            "CONTEXT_UNSUSPEND_FAILED",
            cause=e,
        )
        raise err


def suspend_processing(*, admin: bool = False) -> None:
    """Suspend selected context store."""
    try:
        store = _ensure_context_loaded(admin=admin)
        store.working.suspend()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to suspend context",
            "CONTEXT_SUSPEND_FAILED",
            cause=e,
        )
        raise err


def reset_failure_count(*, admin: bool = False) -> None:
    """Reset error count for selected context store."""
    try:
        store = _ensure_context_loaded(admin=admin)
        if not admin:
            _ensure_not_suspended(admin=admin)
        store.working.reset_failures()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to reset error count",
            "ERROR_COUNT_RESET_FAILED",
            cause=e,
        )
        raise err
