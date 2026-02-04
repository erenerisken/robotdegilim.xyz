"""Public S3 storage API (real S3 + local mock backends)."""

from app.core.settings import get_settings

from .api import delete_file, download_file, s3_file_exists, upload_file
from .common import _mock_dir
from .locks import (
    acquire_lock,
    admin_acquire_lock,
    admin_acquire_op_lock,
    admin_lock_exists,
    admin_lock_status,
    admin_op_lock_exists,
    admin_release_lock,
    admin_release_op_lock,
    admin_validate_lock_token,
    release_lock,
)
from .real_backend import reset_cached_client
from .state import set_run_lock_held


def _reset_s3_client_for_tests() -> None:
    """Reset cached S3 client (used by test suites)."""
    reset_cached_client()


def _set_run_lock_held_for_tests(value: bool) -> None:
    """Set in-memory run lock flag (used by test suites)."""
    set_run_lock_held(value)


__all__ = [
    "acquire_lock",
    "release_lock",
    "upload_file",
    "download_file",
    "s3_file_exists",
    "delete_file",
    "admin_acquire_lock",
    "admin_validate_lock_token",
    "admin_release_lock",
    "admin_lock_status",
    "admin_acquire_op_lock",
    "admin_release_op_lock",
    "admin_lock_exists",
    "admin_op_lock_exists",
    "_reset_s3_client_for_tests",
    "_set_run_lock_held_for_tests",
    "_mock_dir",
    "get_settings",
]
