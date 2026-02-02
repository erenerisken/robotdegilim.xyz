"""IO helpers for scrape-specific local data loading."""

import logging
from typing import Any

from app.core.errors import AppError
from app.core.logging import log_item
from app.core.settings import get_path
from app.storage.local import read_json


def _build_prefix_map(data: dict[str, Any]) -> dict[str, str]:
    """Build department-code to prefix map from serialized department entries."""
    prefix_map: dict[str, str] = {}
    for dept_code, info in data.items():
        if not isinstance(info, dict):
            continue
        prefix = info.get("p")
        if prefix:
            prefix_map[dept_code] = prefix
    return prefix_map


def load_local_dept_prefixes() -> dict[str, str]:
    """Load department prefixes from published file and override file."""
    try:
        data_dir = get_path("DATA_DIR")
        departments_path = data_dir / "published" / "departments.json"
        departments_overrides_path = data_dir / "raw" / "departmentsOverrides.json"
        departments = read_json(departments_path)
        prefixes = _build_prefix_map(departments)
        departments_overrides = read_json(departments_overrides_path)
        overrides = _build_prefix_map(departments_overrides)
        prefixes.update(overrides)
        return prefixes
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to load local department prefixes", "LOAD_LOCAL_DEPT_PREFIXES_FAILED", cause=e)
        log_item("scrape", logging.WARNING, err)
        return {}
