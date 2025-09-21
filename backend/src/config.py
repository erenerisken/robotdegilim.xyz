import os
from pathlib import Path
from dotenv import load_dotenv
import pytz

class app_constants:
    backend_dir = Path(__file__).resolve().parents[1]  # backend/
    try:
        load_dotenv(backend_dir / ".env")
    except Exception:
        pass

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
    log_nte = "robotdegilim.nte"
    log_utils = "robotdegilim.utils"

    # Directories
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
    nte_available_json = "nteAvailable.json"
    nte_list_json = "nteList.json"

    # No department data error message
    noDeptsErrMsg = "No departments data available."

    # No prefix variants
    no_prefix_variants = ["-no course-", "-", ""]

    # Turkey timezone
    TR_TZ = pytz.timezone("Europe/Istanbul")

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
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

    # HTTP default timeout (seconds)
    http_timeout = float(os.environ.get("HTTP_TIMEOUT", "15.0"))

    # Global retry count to unify all HTTP retries
    global_retries = int(os.environ.get("GLOBAL_RETRIES", "10"))

    # Throttling/Backoff tuning (adaptive and circuit-breaker)
    # Scale multiplies all caller-provided base delays (e.g., 1.0 -> unchanged)
    throttle_scale = float(os.environ.get("THROTTLE_SCALE", "0.5"))
    throttle_jitter = float(os.environ.get("THROTTLE_JITTER", "0.25"))
    # Preset scales for runtime toggles
    fast_throttle_scale = float(os.environ.get("FAST_THROTTLE_SCALE", "0.1"))
    slow_throttle_scale = float(os.environ.get("SLOW_THROTTLE_SCALE", "1.0"))

    # Adaptive backoff factors (faster on good network, harsher on failures)
    adaptive_min_factor = float(os.environ.get("ADAPTIVE_MIN_FACTOR", "1.0"))
    adaptive_max_factor = float(os.environ.get("ADAPTIVE_MAX_FACTOR", "8.0"))
    adaptive_grow = float(os.environ.get("ADAPTIVE_GROW", "1.5"))
    adaptive_decay = float(os.environ.get("ADAPTIVE_DECAY", "1.1"))
    adaptive_successes_for_decay = int(os.environ.get("ADAPTIVE_SUCCESSES_FOR_DECAY", "10"))

    # Circuit breaker thresholds (open on sustained errors, cool down longer)
    breaker_fail_threshold = int(os.environ.get("BREAKER_FAIL_THRESHOLD", "10"))
    breaker_window_size = int(os.environ.get("BREAKER_WINDOW_SIZE", "50"))
    breaker_error_rate_threshold = float(os.environ.get("BREAKER_ERROR_RATE_THRESHOLD", "0.5"))
    breaker_cooldown_seconds = int(os.environ.get("BREAKER_COOLDOWN_SECONDS", "120"))
    breaker_probe_interval_seconds = int(os.environ.get("BREAKER_PROBE_INTERVAL_SECONDS", "30"))

    # Static folder: Flask app runs with package root at backend/src, we need absolute path to src/public
    static_folder = backend_dir / "src" / "public"