from app.storage.s3 import download_file, file_exists
from app.core.constants import DEPARTMENTS_FILE
from app.core.paths import downloaded_path
from app.core.errors import AppError
from app.storage.local import read_json

def download_departments():
    try:
        global _departments_path
        if not file_exists(DEPARTMENTS_FILE):
            raise AppError("Departments file does not exist in S3", "DEPARTMENTS_FILE_NOT_FOUND")
        return download_file(DEPARTMENTS_FILE, downloaded_path(DEPARTMENTS_FILE))
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to download departments file", "DOWNLOAD_DEPARTMENTS_FAILED", cause=e)
        raise err
    
def load_departments():
    try:
        result = read_json(downloaded_path(DEPARTMENTS_FILE))
        if not isinstance(result, dict) or not result:
            raise AppError("Departments data loading failed", "LOAD_DEPARTMENTS_FAILED")
        return result
    except Exception as e:
        err= e if isinstance(e, AppError) else AppError("Failed to load departments data", "LOAD_DEPARTMENTS_FAILED", cause=e)
        raise err