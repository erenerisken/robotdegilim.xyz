import json
import shutil
from pathlib import Path

from app.core.errors import AppError


def read_json(path):
    try:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to read json", "READ_JSON_FAILED",context={"path": str(path)}, cause=e)
        raise err


def write_json(path, data):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
        return str(p)
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to write json", "WRITE_JSON_FAILED", context={"path": str(path)}, cause=e)
        raise err


def move_file(src_path, dst_path):
    try:
        src = Path(src_path)
        if not src.exists():
            raise AppError("Failed to move file", "MOVE_FILE_FAILED", context={"src_path": str(src_path), "reason": "Source file does not exist"})
        dst = Path(dst_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return str(dst)
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to move file", "MOVE_FILE_FAILED", context={"src": str(src_path), "dst": str(dst_path)}, cause=e)
        raise err

def delete_file(path):
    try:
        p = Path(path)
        if p.exists():
            p.unlink()
            return True
        return False
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to delete file", "DELETE_FILE_FAILED", context={"path": str(path)}, cause=e)
        raise err