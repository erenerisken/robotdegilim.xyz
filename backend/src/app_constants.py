import os
from pathlib import Path

class app_constants:
    # No department data error message
    noDeptsErrMsg="No departments data available."

    # Email configuration
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Replace with your email
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")  # Replace with your email password
    MAIL_SERVER = "smtp.gmail.com"  # Or another SMTP server
    MAIL_PORT = 587  # Common port for SMTP
    MAIL_DEFAULT_SENDER = MAIL_USERNAME  # Sender address
    MAIL_RECIPIENT = "info.robotdegilim@gmail.com"  # Where to send the email
    MAIL_ERROR_SUBJECT = "RobotDeğilim.xyz Error Alert"

    # s3
    s3_bucket_name="cdn.robotdegilim.xyz"
    aws_access_key_id = os.environ.get('ACCESS_KEY')
    aws_secret_access_key = os.environ.get('SECRET_ACCESS_KEY')
    #aws_region_name = os.environ.get('AWS_REGION')

    # Folder names
    build_folder = "build"
    export_folder = "export"

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

    # output file names
    data_out_name = "data.json"
    departments_out_name = "departments.json"
    musts_out_name = "musts.json"
    last_updated_out_name='lastUpdated.json'
    status_out_name="status.json"
    departments_noprefix_out_name="departmentsNoPrefix.json"
    # input file names
    manual_prefixes_name="manualPrefixes.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 7.0; Win64; x64; rv:3.0b2pre) Gecko/20110203 Firefox/4.0b12pre",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Pragma": "no-cache",
    }

    course_catalog_url = "https://catalog.metu.edu.tr/course.php?prog={dept_code}&course_code={course_code}"
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

    @classmethod
    def init_envs(cls):
        cls.MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Replace with your email
        cls.MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")  # Replace with your email password
        cls.aws_access_key_id = os.environ.get('ACCESS_KEY')
        cls.aws_secret_access_key = os.environ.get('SECRET_ACCESS_KEY')
