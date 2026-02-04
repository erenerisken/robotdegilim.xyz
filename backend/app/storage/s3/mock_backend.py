"""Local filesystem backend that emulates S3 object storage."""

from __future__ import annotations

from .common import _mock_path


def read_object_bytes(key: str) -> bytes | None:
    """Read object bytes from local mock storage."""
    path = _mock_path(key)
    if not path.exists():
        return None
    return path.read_bytes()


def write_object_bytes(key: str, content: bytes) -> None:
    """Write object bytes to local mock storage atomically."""
    path = _mock_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(content)
    tmp_path.replace(path)


def object_exists(key: str) -> bool:
    """Check object existence in local mock storage."""
    return _mock_path(key).exists()


def delete_object(key: str) -> bool:
    """Delete object from local mock storage and return whether it existed."""
    path = _mock_path(key)
    if not path.exists():
        return False
    path.unlink()
    return True
