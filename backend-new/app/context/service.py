"""Context state service for loading, mutating, and publishing app context."""

from app.context.schema import AppContext
from app.core.constants import CONTEXT_KEY, RequestType
from app.core.errors import AppError
from app.core.paths import downloaded_path, published_path, staged_path
from app.storage.local import move_file, read_json, write_json
from app.storage.s3 import download_file, file_exists, upload_file

_original_context: AppContext | None = None
_copy_context: AppContext | None = None
_loaded: bool = False

def load_context() -> None:
    """Load context from storage once and keep original/copy snapshots in memory."""
    global _original_context, _copy_context, _loaded
    try:
        if not _loaded:
            if file_exists(CONTEXT_KEY):
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


def publish_context() -> None:
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


def queue_request(request_type: RequestType) -> bool:
    """Queue a request type if queueing is supported and it is not already queued."""
    try:
        global _copy_context, _loaded
        if request_type == RequestType.SCRAPE:
            return False
        if not _loaded:
            load_context()
        if _copy_context is None:
            raise AppError("Context copy is not loaded", "CONTEXT_NOT_LOADED")
        if _copy_context.in_queue[request_type.value]:
            return False
        _copy_context.queue.append(request_type.value)
        _copy_context.in_queue[request_type.value] = True
        return True
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to queue request", "REQUEST_QUEUE_FAILED", cause=e)
        raise err


def get_next_request(request_type: RequestType) -> tuple[bool, RequestType]:
    """Return the next queued request or the incoming request when queue is empty."""
    try:
        global _copy_context, _loaded
        if not _loaded:
            load_context()
        if _copy_context is None:
            raise AppError("Context copy is not loaded", "CONTEXT_NOT_LOADED")
        if not _copy_context.queue:
            return False, request_type
        next_request = _copy_context.queue.pop(0)
        _copy_context.in_queue[next_request] = False
        return True, RequestType(next_request)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to get next request", "REQUEST_GET_FAILED", cause=e)
        raise err
