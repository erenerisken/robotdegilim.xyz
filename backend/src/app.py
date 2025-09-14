from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
import logging

from utils.timezone import TZ_TR, time_converter_factory, TzTimedRotatingFileHandler
from pathlib import Path
# Load backend/.env early in dev so env vars are available before importing app_constants
try:
    from dotenv import load_dotenv
    # Ensure we load the .env located under backend/.env regardless of CWD
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
except Exception:
    pass
from app_constants import app_constants
from scrape.scrape import run_scrape
from musts.musts import run_musts
from utils.emailer import get_email_handler
from utils.helpers import is_idle, get_s3_client
from ops.exceptions import RecoverException # do not delete this line

# Set up structured logging split: app, jobs, and errors
fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
fmt.converter = time_converter_factory(TZ_TR)

parent_logger = logging.getLogger(app_constants.log_parent)
app_logger = logging.getLogger(app_constants.log_app)
scrape_logger = logging.getLogger(app_constants.log_scrape)
musts_logger = logging.getLogger(app_constants.log_musts)

parent_logger.setLevel(logging.INFO)
app_logger.setLevel(logging.INFO)
scrape_logger.setLevel(logging.INFO)
musts_logger.setLevel(logging.INFO)

# app.log (INFO+) — rotate daily at TR midnight, keep 5 days
_log_days = 5
app_file = app_constants.app_log_file
if not any(isinstance(h, TzTimedRotatingFileHandler) and getattr(h, 'baseFilename', '').endswith(app_file) for h in app_logger.handlers):
    h = TzTimedRotatingFileHandler(app_file, when='midnight', interval=1, backupCount=_log_days, encoding=app_constants.log_encoding)
    h.setLevel(logging.INFO)
    h.setFormatter(fmt)
    app_logger.addHandler(h)

# jobs.log (INFO+) for scrape and musts — rotate daily at TR midnight, keep 3 days
jobs_file = app_constants.jobs_log_file
for job_logger in (scrape_logger, musts_logger):
    if not any(isinstance(h, TzTimedRotatingFileHandler) and getattr(h, 'baseFilename', '').endswith(jobs_file) for h in job_logger.handlers):
        h = TzTimedRotatingFileHandler(jobs_file, when='midnight', interval=1, backupCount=_log_days, encoding=app_constants.log_encoding)
        h.setLevel(logging.INFO)
        h.setFormatter(fmt)
        job_logger.addHandler(h)

# error.log (ERROR+) on parent so children propagate up — rotate daily at TR midnight, keep 3 days
err_file = app_constants.error_log_file
if not any(isinstance(h, TzTimedRotatingFileHandler) and getattr(h, 'baseFilename', '').endswith(err_file) for h in parent_logger.handlers):
    h = TzTimedRotatingFileHandler(err_file, when='midnight', interval=1, backupCount=_log_days, encoding=app_constants.log_encoding)
    h.setLevel(logging.ERROR)
    h.setFormatter(fmt)
    parent_logger.addHandler(h)

# Email handler (ERROR+) on parent if configured
email_handler = get_email_handler()
if email_handler and not any(isinstance(h, type(email_handler)) for h in parent_logger.handlers):
    email_handler.setLevel(logging.ERROR)
    parent_logger.addHandler(email_handler)

# Use app logger for this module
_logger = app_logger

# Initialize Flask app
app = Flask(__name__)
api = Api(app)
cors = CORS(app)

# simple in-process flags
queued_musts_after_scrape = False
depts_data_available = False

@app.route('/')
def index():
    """Root endpoint for API server (no static files)."""
    return {"service": "robotdegilim-backend", "endpoints": ["/run-scrape", "/run-musts", "/status"]}, 200

class RunScrape(Resource):
    def get(self):
        global depts_data_available, queued_musts_after_scrape
        try:
            if run_scrape() == "busy":
                return {"status": "System is busy"}, 200
            depts_data_available = True
            # If a musts run was queued during busy period, run it now
            if queued_musts_after_scrape:
                _logger.info("musts run was queued; running after scrape completion")
                try:
                    result = run_musts()
                    if result != "busy":
                        queued_musts_after_scrape = False
                        return {"status": "Scraping completed; musts completed successfully"}, 200
                    # Very unlikely: still busy
                    return {"status": "Scraping completed; musts still busy"}, 200
                except Exception as e:
                    _logger.error(f"queued musts run failed: {e}")
                    return {"status": "Scraping completed; musts failed"}, 500
            return {"status": "Scraping completed successfully"}, 200
        except Exception as e:
            _logger.error(str(e))
            return {"error": "Error running scrape process"}, 500

class RunMusts(Resource):
    def get(self):
        global queued_musts_after_scrape
        global depts_data_available
        try:
            # If departments data is not ready yet, queue and exit
            if not depts_data_available:
                if not queued_musts_after_scrape:
                    queued_musts_after_scrape = True
                    return {"status": "Departments data unavailable; musts queued to run after scrape"}, 200
                return {"status": "Musts already queued; waiting for scrape to produce data"}, 200

            if run_musts() == "busy":
                if not queued_musts_after_scrape:
                    queued_musts_after_scrape = True
                    return {"status": "System busy; musts queued to run after scrape"}, 200
                return {"status": "System busy; musts already queued"}, 200
            queued_musts_after_scrape = False
            return {"status": "Get musts completed successfully"}, 200
        except Exception as e:
            _logger.error(str(e))
            if app_constants.noDeptsErrMsg in str(e):
                depts_data_available = False
                queued_musts_after_scrape = True
                _logger.info("departments data missing; queued musts until after scrape")
                return {"status": "Departments data missing; musts queued to run after next scrape"}, 200
            return {"error": "Error running get musts process"}, 500

# Add API resources
api.add_resource(RunScrape, '/run-scrape')
api.add_resource(RunMusts, '/run-musts')

@app.route('/status')
def status():
    """Report backend readiness and S3 status.json busy/idle state."""
    try:
        s3 = get_s3_client()
        return {
            "status": "idle" if is_idle(s3) else "busy",
            "queued_musts": queued_musts_after_scrape,
            "depts_data_available": depts_data_available,
        }, 200
    except Exception as e:
        _logger.error(f"status check failed: {e}")
        return {"status": "unknown", "error": "status check failed"}, 500
