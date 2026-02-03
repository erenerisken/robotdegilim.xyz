"""Application constants and shared enum types."""

from enum import Enum


class RequestType(str, Enum):
    """Supported top-level request types handled by the backend."""

    ROOT = "root"
    SCRAPE = "scrape"
    MUSTS = "musts"


# Scrape process constants
OIBS64_URL: str = "https://oibs2.metu.edu.tr/View_Program_Course_Details_64/main.php"
COURSE_CATALOG_URL: str = "https://catalog.metu.edu.tr/course.php?prog={dept_code}&course_code={course_code}"
NO_PREFIX_VARIANTS: tuple[str, str] = ("<no-course>", "<prefix-not-found>")
DAYS_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

# Data directory names
DATA_SUBDIR_RAW = "raw"
DATA_SUBDIR_STAGED = "staged"
DATA_SUBDIR_PUBLISHED = "published"
DATA_SUBDIR_DOWNLOADED = "downloaded"
DATA_SUBDIR_CACHE = "cache"

# Shared file keys / names
CONTEXT_KEY = "context.json"
SCRAPE_CACHE_FILE = "scrape_cache.json"
MUSTS_CACHE_FILE = "musts_cache.json"
MUSTS_FILE = "musts.json"
DEPARTMENTS_FILE = "departments.json"
DEPARTMENTS_NO_PREFIX_FILE = "departmentsNoPrefix.json"
DEPARTMENTS_OVERRIDES_FILE = "departmentsOverrides.json"
DATA_FILE = "data.json"
LAST_UPDATED_FILE = "lastUpdated.json"

# Mock S3 filesystem names
S3_MOCK_DIR_NAME = "s3-mock"
S3_LOCK_FILE = "lockfile.lock"

# Logger names
LOGGER_APP = "app"
LOGGER_SCRAPE = "scrape"
LOGGER_MUSTS = "musts"
LOGGER_ERROR = "error"

# Log file names
LOG_FILE_APP = "app.log"
LOG_FILE_SCRAPE = "scrape.log"
LOG_FILE_MUSTS = "musts.log"
LOG_FILE_ERROR = "error.log"
