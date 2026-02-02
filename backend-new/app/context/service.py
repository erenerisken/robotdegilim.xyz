from app.context.schema import AppContext, S3_CONTEXT_KEY
from app.storage.s3 import download_file, upload_file, file_exists
from app.storage.local import move_file, read_json, write_json
from app.core.settings import get_path
from app.core.errors import AppError
from app.core.constants import RequestType

_original_context:AppContext=None
_copy_context:AppContext=None
_loaded:bool=False

def _local_download_path():
    data_dir = get_path("DATA_DIR")
    return data_dir / "downloaded" / S3_CONTEXT_KEY

def _local_staged_path():
    data_dir = get_path("DATA_DIR")
    return data_dir / "staged" / S3_CONTEXT_KEY

def _local_published_path():
    data_dir = get_path("DATA_DIR")
    return data_dir / "published" / S3_CONTEXT_KEY

def load_context() -> None:
    global _original_context, _copy_context, _loaded
    try:
        if not _loaded:
            if file_exists(S3_CONTEXT_KEY):
                local_path = _local_download_path()
                download_file(S3_CONTEXT_KEY, local_path)
                data = read_json(local_path)
                _original_context = AppContext(**data)
                _copy_context = _original_context.model_copy(deep=True)
            else:
                _original_context = AppContext()
                _copy_context = _original_context.model_copy(deep=True)
            _loaded = True
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to load context", "CONTEXT_LOAD_FAILED",cause=e)
        raise err

def publish_context() -> None:
    global _original_context, _copy_context, _loaded
    try:
        if  _loaded:
            _original_context = _copy_context.model_copy(deep=True)
            local_staged_path = _local_staged_path()
            write_json(local_staged_path, _original_context.model_dump())
            upload_file(local_staged_path, S3_CONTEXT_KEY)
            move_file(local_staged_path, _local_published_path())
            detach_context()
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to publish context", "CONTEXT_PUBLISH_FAILED", cause=e)
        raise err

def detach_context() -> None:
    global _original_context, _copy_context, _loaded
    _original_context = None
    _copy_context = None
    _loaded = False

def queue_request(request_type: RequestType) -> None:
    try:
        global _copy_context, _loaded
        if request_type == RequestType.SCRAPE:
            return False
        if not _loaded:
            load_context()
        if _copy_context.in_queue[request_type.value]:
            return False
        _copy_context.queue.append(request_type.value)
        _copy_context.in_queue[request_type.value] = True
        return True
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to queue request", "REQUEST_QUEUE_FAILED", cause=e)
        raise err

def get_next_request(request_type):
    try:
        global _copy_context, _loaded
        if not _loaded:
            load_context()
        if not _copy_context.queue:
            return False, request_type
        next_request = _copy_context.queue.pop(0)
        _copy_context.in_queue[next_request] = False
        return True, RequestType(next_request)
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to get next request", "REQUEST_GET_FAILED", cause=e)
        raise err