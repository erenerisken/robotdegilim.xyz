from app.context.schema import AppContext, ContextUpdate, ContextUpdateType, S3_CONTEXT_KEY
from app.storage.s3 import download_file, upload_file, file_exists
from app.storage.local import move_file, read_json, write_json
from app.core.settings import get_path
from app.core.errors import AppError

_context:AppContext=None
_updates:list[ContextUpdate]=[]

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
    global _context
    try:
        if _context is None:
            if file_exists(S3_CONTEXT_KEY):
                local_path = _local_download_path()
                download_file(S3_CONTEXT_KEY, local_path)
                data = read_json(local_path)
                _context = AppContext(**data)
            else:
                _context = AppContext()
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to load context", "CONTEXT_LOAD_FAILED",cause=e)
        raise err

def publish_context() -> None:
    global _context
    try:
        if _context:
            local_staged_path = _local_staged_path()
            write_json(local_staged_path, _context.model_dump())
            upload_file(local_staged_path, S3_CONTEXT_KEY)
            move_file(local_staged_path, _local_published_path())
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to publish context", "CONTEXT_PUBLISH_FAILED", cause=e)
        raise err

def detach_context() -> None:
    global _context
    _context = None

def queue_request(request_type):
    # to be implemented
    pass

def get_next_request(request_type):
    # to be implemented
    pass

def apply_context_updates() -> None:
    pass

def update_context(update_type: ContextUpdateType, **kwargs) -> None:
    global _updates
    update = ContextUpdate(update_type=update_type, **kwargs)
    _updates.append(update)



