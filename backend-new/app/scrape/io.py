from app.core.settings import get_setting
from app.utils.io import read_json
from app.core.logging import get_logger
from app.core.errors import ScrapeError

def load_local_dept_prefixes():
    logger= get_logger("scrape")
    try:
        data_dir= get_setting("DATA_DIR")
        departments_path= data_dir /"published" / "departments.json"
        departments_overrides_path= data_dir /"raw" / "departmentsOverrides.json"
        departments = read_json(departments_path)
        departments_overrides = read_json(departments_overrides_path)
        departments.update(departments_overrides)
        return departments
    except Exception as e:
        err=ScrapeError(
            message="Failed to load local department prefixes", cause=e
        )
        logger.warning(err)