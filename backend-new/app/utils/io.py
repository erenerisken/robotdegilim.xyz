import json
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
