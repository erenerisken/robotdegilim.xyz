import os
from pathlib import Path

from pytz import timezone


class app_constants:
    # Email configuration
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")  # Replace with your email
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")  # Replace with your email password
    MAIL_SERVER = "smtp.gmail.com"  # Or another SMTP server
    MAIL_PORT = 587  # Common port for SMTP
    MAIL_DEFAULT_SENDER = MAIL_USERNAME  # Sender address
    MAIL_RECIPIENT = "info.robotdegilim@gmail.com"  # Where to send the email
    MAIL_ERROR_SUBJECT = "Robotdegilim.xyz Error Alert"

    # s3
    s3_bucket_name = "cdn.robotdegilim.xyz"
    aws_access_key_id = os.environ.get("ACCESS_KEY")
    aws_secret_access_key = os.environ.get("SECRET_ACCESS_KEY")
    # aws_region_name = os.environ.get('AWS_REGION')

    # Log file names
    app_log_file = "app.log"
    jobs_log_file = "jobs.log"
    error_log_file = "error.log"
    log_encoding = "utf-8"

    # Logger names
    log_parent = "robotdegilim"
    log_app = "robotdegilim.app"
    log_scrape = "robotdegilim.scrape"
    log_musts = "robotdegilim.musts"
    log_utils = "robotdegilim.utils"

    # Directories
    backend_dir = Path(__file__).resolve().parents[1]  # backend/
    log_dir = backend_dir / "storage" / "logs"
    data_dir = backend_dir / "storage" / "data"

    # json file names
    data_json = "data.json"
    departments_json = "departments.json"
    musts_json = "musts.json"
    last_updated_json = "lastUpdated.json"
    status_json = "status.json"
    departments_noprefix_json = "departmentsNoPrefix.json"
    manual_prefixes_json = "manualPrefixes.json"

    # No department data error message
    noDeptsErrMsg = "No departments data available."

    # No prefix variants
    no_prefix_variants = ["-no course-", "-", ""]

    # Turkey timezone
    TR_TZ = timezone("Europe/Istanbul")

    # Web scraping
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
    }

    course_catalog_url = (
        "https://catalog.metu.edu.tr/course.php?prog={dept_code}&course_code={course_code}"
    )
    department_catalog_url = "http://catalog.metu.edu.tr/program.php?fac_prog={dept_code}"
    oibs64_url = "https://oibs2.metu.edu.tr/View_Program_Course_Details_64/main.php"

    days_dict = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    # API / Runtime config
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")  # comma-separated or *
    log_json = os.environ.get("LOG_JSON", "false").lower() in ("1", "true", "yes")
    app_version = os.environ.get("APP_VERSION", "0.1.0")
