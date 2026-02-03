"""Context state service for loading, mutating, and publishing app context."""
import logging

from app.context.schema import AppContext
from app.core.constants import CONTEXT_KEY, LOGGER_APP, RequestType
from app.core.errors import AppError
from app.core.settings import get_settings
from app.core.logging import log_item
from app.core.paths import downloaded_path, published_path, staged_path
from app.storage.local import move_file, read_json, write_json
from app.storage.s3 import download_file, s3_file_exists, upload_file

_original_context: AppContext | None = None
_copy_context: AppContext | None = None
_loaded: bool = False

def load_context_state() -> None:
    """Load context from storage once and keep original/copy snapshots in memory."""
    global _original_context, _copy_context, _loaded
    try:
        if not _loaded:
            if s3_file_exists(CONTEXT_KEY):
                local_path = downloaded_path(CONTEXT_KEY)
                download_file(CONTEXT_KEY, local_path)
                data = read_json(local_path)
                _original_context = AppContext(**data)
                _copy_context = _original_context.model_copy(deep=True)
            else:
                _original_context = AppContext()
                _copy_context = _original_context.model_copy(deep=True)
            _loaded = True
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to load context", "CONTEXT_LOAD_FAILED", cause=e)
        raise err


def publish_context_state() -> None:
    """Persist the current context copy and mark it as published locally and in S3."""
    global _original_context, _copy_context, _loaded
    try:
        if _loaded and _copy_context is not None:
            _original_context = _copy_context.model_copy(deep=True)
            local_staged_path = staged_path(CONTEXT_KEY)
            write_json(local_staged_path, _original_context.model_dump())
            upload_file(local_staged_path, CONTEXT_KEY)
            move_file(local_staged_path, published_path(CONTEXT_KEY))
            detach_context()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to publish context", "CONTEXT_PUBLISH_FAILED", cause=e)
        raise err


def detach_context() -> None:
    """Clear in-memory context state."""
    global _original_context, _copy_context, _loaded
    _original_context = None
    _copy_context = None
    _loaded = False


def enqueue_request(request_type: RequestType) -> bool:
    """Queue a request type if queueing is supported and it is not already queued."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _ensure_not_suspended()
        return _copy_context.enqueue(request_type)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to queue request", "REQUEST_QUEUE_FAILED", cause=e)
        raise err


def resolve_request(request_type: RequestType) -> tuple[bool, RequestType]:
    """Return the next queued request or the incoming request when queue is empty."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _ensure_not_suspended()
        next_request = _copy_context.dequeue()
        if next_request is None:
            return False, request_type
        return True, next_request
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to get next request", "REQUEST_GET_FAILED", cause=e)
        raise err

def record_failure() -> None:
    """Increment the error count in the context."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _ensure_not_suspended()
        if _copy_context.mark_failure(get_settings().CONTEXT_MAX_ERRORS):
            log_item(LOGGER_APP, logging.WARNING, AppError("AppContext has been suspended due to exceeding maximum error count", "CONTEXT_SUSPENDED"))
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to increment error count", "ERROR_INCREMENT_FAILED", cause=e)
        raise err
    
def record_success() -> None:
    """Decrement the error count in the context."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _ensure_not_suspended()
        _copy_context.mark_success()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to decrement error count", "ERROR_DECREMENT_FAILED", cause=e)
        raise err

def _ensure_context_loaded() -> None:
    """Ensure that the context is loaded in memory."""
    global _loaded, _copy_context, _original_context
    if not _loaded:
        load_context_state()
    if _copy_context is None or _original_context is None:
        raise AppError("Context is not loaded", "CONTEXT_NOT_LOADED")
    
def clear_queue() -> None:
    """Clear the request queue in the context."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _ensure_not_suspended()
        _copy_context.clear_queue()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to clear request queue", "QUEUE_CLEAR_FAILED", cause=e)
        raise err
    
def _ensure_not_suspended() -> None:
    """Ensure that the context is not suspended."""
    global _copy_context
    _ensure_context_loaded()
    if _copy_context.suspended:
        raise AppError("AppContext is suspended", "CONTEXT_SUSPENDED")

def unsuspend_processing() -> None:
    """Unsuspend the context."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _copy_context.unsuspend()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to unsuspend context", "CONTEXT_UNSUSPEND_FAILED", cause=e)
        raise err
    
def suspend_processing() -> None:
    """Suspend the context immediately."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _copy_context.suspend()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to suspend context", "CONTEXT_SUSPEND_FAILED", cause=e)
        raise err
    
def reset_failure_count() -> None:
    """Reset the error count in the context to zero."""
    try:
        global _copy_context
        _ensure_context_loaded()
        _copy_context.reset_failures()
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to reset error count", "ERROR_COUNT_RESET_FAILED", cause=e)
        raise err
