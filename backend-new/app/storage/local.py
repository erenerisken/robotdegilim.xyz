import json
import shutil
from pathlib import Path

from app.core.errors import StorageError


def read_json(path):
    try:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:
        raise StorageError(message="Failed to read json", context={"path": str(path)}, cause=e)


def write_json(path, data):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
        return str(p)
    except Exception as e:
        raise StorageError(message="Failed to write json", context={"path": str(path)}, cause=e)


def move_file(src_path, dst_path):
    try:
        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")
        dst = Path(dst_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return str(dst)
    except Exception as e:
        raise StorageError(message="Failed to move file", context={"src": str(src_path), "dst": str(dst_path)}, cause=e)

def delete_file(path):
    try:
        p = Path(path)
        if p.exists():
            p.unlink()
            return True
        return False
    except Exception as e:
        raise StorageError(message="Failed to delete file", context={"path": str(path)}, cause=e)