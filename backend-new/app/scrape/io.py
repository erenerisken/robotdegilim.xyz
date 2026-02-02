import logging

from app.core.settings import get_path
from app.storage.local import read_json
from app.core.logging import log_item
from app.core.errors import AppError

def _build_prefix_map(data):
    prefix_map = {}
    for dept_code, info in data.items():
        prefix = info.get("p")
        if prefix:
            prefix_map[dept_code] = prefix
    return prefix_map

def load_local_dept_prefixes():
    try:
        data_dir = get_path("DATA_DIR")
        departments_path = data_dir / "published" / "departments.json"
        departments_overrides_path = data_dir / "raw" / "departmentsOverrides.json"
        departments = read_json(departments_path)
        prefixes= _build_prefix_map(departments)
        departments_overrides = read_json(departments_overrides_path)
        overrides= _build_prefix_map(departments_overrides)
        prefixes.update(overrides)
        return prefixes
    except Exception as e:
        err=e if isinstance(e, AppError) else AppError("Failed to load local department prefixes","LOAD_LOCAL_DEPT_PREFIXES_FAILED", cause=e)
        log_item("scrape", logging.WARNING, err.to_log())
        return {}
