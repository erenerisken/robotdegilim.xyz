"""Path helpers for data directory subfolders and common file locations."""

from pathlib import Path

from app.core.constants import (
    DATA_SUBDIR_CACHE,
    DATA_SUBDIR_DOWNLOADED,
    DATA_SUBDIR_PUBLISHED,
    DATA_SUBDIR_RAW,
    DATA_SUBDIR_STAGED,
)
from app.core.settings import get_path


def data_dir() -> Path:
    """Return the configured data directory path."""
    return get_path("DATA_DIR")


def _subdir(name: str) -> Path:
    """Return a direct child directory of data directory."""
    return data_dir() / name


def raw_dir() -> Path:
    """Return raw data directory."""
    return _subdir(DATA_SUBDIR_RAW)


def staged_dir() -> Path:
    """Return staged data directory."""
    return _subdir(DATA_SUBDIR_STAGED)


def published_dir() -> Path:
    """Return published data directory."""
    return _subdir(DATA_SUBDIR_PUBLISHED)


def downloaded_dir() -> Path:
    """Return downloaded data directory."""
    return _subdir(DATA_SUBDIR_DOWNLOADED)


def cache_dir() -> Path:
    """Return cache data directory."""
    return _subdir(DATA_SUBDIR_CACHE)


def raw_path(filename: str) -> Path:
    """Return path under raw data directory."""
    return raw_dir() / filename


def staged_path(filename: str) -> Path:
    """Return path under staged data directory."""
    return staged_dir() / filename


def published_path(filename: str) -> Path:
    """Return path under published data directory."""
    return published_dir() / filename


def downloaded_path(filename: str) -> Path:
    """Return path under downloaded data directory."""
    return downloaded_dir() / filename


def cache_path(filename: str) -> Path:
    """Return path under cache data directory."""
    return cache_dir() / filename


def log_dir() -> Path:
    """Return configured log directory path."""
    return get_path("LOG_DIR")
