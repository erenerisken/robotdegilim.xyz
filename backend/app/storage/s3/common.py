"""Shared helpers for S3 real/mock backends."""

from pathlib import Path

from app.core.constants import S3_MOCK_DIR_NAME
from app.core.errors import AppError
from app.core.settings import get_settings


def _is_real_s3_enabled() -> bool:
    """Return whether real S3 mode is enabled via settings."""
    settings = get_settings()
    bucket = str(getattr(settings, "S3_BUCKET", "") or "").strip()
    return bool(bucket)


def _normalize_key(key: str) -> str:
    """Normalize and validate storage key as a safe relative path-like string."""
    raw = str(key).strip()
    if not raw:
        raise AppError("Invalid key path.", "S3_INVALID_KEY", context={"key": key})
    key_path = Path(raw)
    if key_path.is_absolute() or ".." in key_path.parts:
        raise AppError("Invalid key path.", "S3_INVALID_KEY", context={"key": key})
    normalized = "/".join(part for part in key_path.parts if part not in ("", "."))
    if not normalized:
        raise AppError("Invalid key path.", "S3_INVALID_KEY", context={"key": key})
    return normalized


def _s3_bucket() -> str:
    """Return configured S3 bucket or raise when missing."""
    settings = get_settings()
    bucket = str(getattr(settings, "S3_BUCKET", "") or "").strip()
    if not bucket:
        raise AppError("S3 bucket is not configured.", "S3_BUCKET_NOT_CONFIGURED")
    return bucket


def _mock_dir() -> Path:
    """Return local directory that emulates S3 storage in mock mode."""
    base = Path(__file__).resolve().parents[3] / S3_MOCK_DIR_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def _mock_path(key: str) -> Path:
    """Resolve object key to a filesystem path for mock mode."""
    return _mock_dir() / _normalize_key(key)
