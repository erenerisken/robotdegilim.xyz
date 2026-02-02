"""Application constants and shared enum types."""

from enum import Enum


class RequestType(str, Enum):
    """Supported top-level request types handled by the backend."""

    SCRAPE = "scrape"
    ROOT = "root"


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
