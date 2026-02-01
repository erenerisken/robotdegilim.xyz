from app.core.settings import get_path
from app.storage.local import read_json
from app.core.logging import get_logger
from app.core.errors import ScrapeError

def _build_prefix_map(data):
    prefix_map = {}
    for dept_code, info in data.items():
        prefix = info.get("p")
        if prefix:
            prefix_map[dept_code] = prefix
    return prefix_map

def load_local_dept_prefixes():
    logger= get_logger("scrape")
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
        err=ScrapeError(
            message="Failed to load local department prefixes", cause=e
        )
        logger.warning(err.to_log())
