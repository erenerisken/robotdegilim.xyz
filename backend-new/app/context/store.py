from app.context.context import AppContext
from app.storage.s3 import download_file, upload_file, head
from app.storage.local import move_file, read_json, write_json
from app.core.settings import get_path
from app.core.errors import AppError

CONTEXT_KEY = "context.json"


def _local_download_path():
    data_dir = get_path("DATA_DIR")
    return data_dir / "downloaded" / CONTEXT_KEY

def _local_staged_path():
    data_dir = get_path("DATA_DIR")
    return data_dir / "staged" / CONTEXT_KEY

def _local_published_path():
    data_dir = get_path("DATA_DIR")
    return data_dir / "published" / CONTEXT_KEY


def get_context() -> AppContext:
    try:
        if head(CONTEXT_KEY):
            local_path = _local_download_path()
            download_file(CONTEXT_KEY, local_path)
            data = read_json(local_path)
            return AppContext(**data)
        else:
            return AppContext()
    except Exception as e:
        raise AppError("Failed to get context", "APP_CONTEXT_GET_ERROR",cause=e)

def save_context(ctx: AppContext) -> None:
    try:
        local_staged_path = _local_staged_path()
        write_json(local_staged_path, ctx.model_dump())
        upload_file(local_staged_path, CONTEXT_KEY)
        move_file(local_staged_path, _local_published_path())
    except Exception as e:
        raise AppError("Failed to save context", "APP_CONTEXT_SAVE_ERROR", cause=e)
