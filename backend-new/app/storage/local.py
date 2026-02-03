"""Local filesystem helpers for JSON IO and file operations."""

import json
import shutil
from pathlib import Path
from typing import Any

from app.core.errors import AppError
from app.core.paths import downloaded_dir


def read_json(path: str | Path) -> dict[str, Any]:
    """Read JSON object from path; return empty dict if file is missing/invalid type."""
    try:
        p = Path(path)
        if not p.exists():
            return {}
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to read json", "READ_JSON_FAILED", context={"path": str(path)}, cause=e)
        raise err


def write_json(path: str | Path, data: Any) -> str:
    """Write data as JSON file and return written path as string."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
        return str(p)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to write json", "WRITE_JSON_FAILED", context={"path": str(path)}, cause=e)
        raise err


def move_file(src_path: str | Path, dst_path: str | Path) -> str:
    """Move a file to a destination path and return destination as string."""
    try:
        src = Path(src_path)
        if not src.exists():
            raise AppError("Failed to move file", "MOVE_FILE_FAILED", context={"src_path": str(src_path), "reason": "Source file does not exist"})
        dst = Path(dst_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return str(dst)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to move file", "MOVE_FILE_FAILED", context={"src": str(src_path), "dst": str(dst_path)}, cause=e)
        raise err


def delete_file(path: str | Path) -> bool:
    """Delete a file if it exists and return whether deletion happened."""
    try:
        p = Path(path)
        if p.exists():
            p.unlink()
            return True
        return False
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to delete file", "DELETE_FILE_FAILED", context={"path": str(path)}, cause=e)
        raise err


def clear_downloaded_dir() -> int:
    """Delete all files/directories under downloaded dir and return removed entry count."""
    try:
        root = downloaded_dir()
        if not root.exists():
            return 0

        removed = 0
        # Delete children before parents so nested directories can be removed safely.
        for entry in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if entry.is_file():
                entry.unlink()
                removed += 1
            elif entry.is_dir():
                entry.rmdir()
                removed += 1
        return removed
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to clear downloaded directory",
            "CLEAR_DOWNLOADED_DIR_FAILED",
            context={"path": str(downloaded_dir())},
            cause=e,
        )
        raise err
