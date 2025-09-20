import datetime
import uuid
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import logging
import os
from werkzeug.exceptions import HTTPException
from src.errors import AppError

from src.utils.timezone import TZ_TR, time_converter_factory, TzTimedRotatingFileHandler
from pathlib import Path

# Load backend/.env early in dev so env vars are available before importing app_constants
try:
    from dotenv import load_dotenv

    # Ensure we load the .env located under backend/.env regardless of CWD
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass
from src.config import app_constants
from src.scrape.scrape import run_scrape
from src.musts.musts import run_musts
from src.nte.nte import run_nte
from src.utils.emailer import get_email_handler
from src.utils.s3 import get_s3_client
from src.services.status_service import get_status, set_status, init_status, set_busy, set_idle
from src.utils.logging import JsonFormatter
from src.utils.timing import set_speed_mode, get_speed_mode

# Set up structured logging split: app, jobs, and errors
fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
fmt.converter = time_converter_factory(TZ_TR)

parent_logger = logging.getLogger(app_constants.log_parent)
app_logger = logging.getLogger(app_constants.log_app)
scrape_logger = logging.getLogger(app_constants.log_scrape)
musts_logger = logging.getLogger(app_constants.log_musts)
nte_logger = logging.getLogger(app_constants.log_nte)

_lvl = getattr(logging, app_constants.log_level, logging.INFO)
parent_logger.setLevel(_lvl)
app_logger.setLevel(_lvl)
scrape_logger.setLevel(_lvl)
musts_logger.setLevel(_lvl)
nte_logger.setLevel(_lvl)

# app.log (INFO+) - rotate daily at TR midnight, keep 5 days
_log_days = 5
_log_dir = app_constants.log_dir
_log_dir.mkdir(parents=True, exist_ok=True)

app_file = str(_log_dir / app_constants.app_log_file)
if not any(
    isinstance(h, TzTimedRotatingFileHandler)
    and os.path.basename(getattr(h, "baseFilename", "")) == app_constants.app_log_file
    for h in app_logger.handlers
):
    h = TzTimedRotatingFileHandler(
        app_file,
        when="midnight",
        interval=1,
        backupCount=_log_days,
        encoding=app_constants.log_encoding,
    )
    h.setLevel(logging.INFO)
    h.setFormatter(fmt)
    app_logger.addHandler(h)

# jobs.log (INFO+) for scrape, musts and nte - rotate daily at TR midnight, keep 5 days
jobs_file = str(_log_dir / app_constants.jobs_log_file)
for job_logger in (scrape_logger, musts_logger, nte_logger):
    if not any(
        isinstance(h, TzTimedRotatingFileHandler)
        and os.path.basename(getattr(h, "baseFilename", "")) == app_constants.jobs_log_file
        for h in job_logger.handlers
    ):
        h = TzTimedRotatingFileHandler(
            jobs_file,
            when="midnight",
            interval=1,
            backupCount=_log_days,
            encoding=app_constants.log_encoding,
        )
        h.setLevel(logging.INFO)
        h.setFormatter(fmt)
        job_logger.addHandler(h)

# error.log (ERROR+) on parent so children propagate up - rotate daily at TR midnight, keep 5 days
err_file = str(_log_dir / app_constants.error_log_file)
if not any(
    isinstance(h, TzTimedRotatingFileHandler)
    and os.path.basename(getattr(h, "baseFilename", "")) == app_constants.error_log_file
    for h in parent_logger.handlers
):
    h = TzTimedRotatingFileHandler(
        err_file,
        when="midnight",
        interval=1,
        backupCount=_log_days,
        encoding=app_constants.log_encoding,
    )
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

# Optional JSON log formatting
if app_constants.log_json:
    jf = JsonFormatter(converter=fmt.converter)
    for lg in (app_logger, scrape_logger, musts_logger, nte_logger, parent_logger):
        for h in lg.handlers:
            h.setFormatter(jf)

# Initialize status defaults in S3 at startup
try:
    s3 = get_s3_client()
    init_status(s3)
except Exception as e:
    app_logger.warning(f"Could not initialize status in S3, error: {str(e)}")

# Initialize Flask app (serve static assets from src/public under /static)
app = Flask(
    __name__,
    static_folder=app_constants.static_folder,
    static_url_path='/'
)
api = Api(app)
origins = app_constants.allowed_origins
if origins and origins != "*":
    cors = CORS(
        app, resources={r"/*": {"origins": [o.strip() for o in origins.split(",") if o.strip()]}}
    )
else:
    cors = CORS(app)


@app.before_request
def _access_log_start():
    request._start_time = datetime.datetime.now()
    request._request_id = uuid.uuid4().hex


@app.after_request
def _access_log_end(response):
    try:
        start = getattr(request, "_start_time", None)
        if start:
            duration_ms = int((datetime.datetime.now() - start).total_seconds() * 1000)
        else:
            duration_ms = -1
        app_logger.info(
            f"access method={request.method} path={request.path} status={response.status_code} duration_ms={duration_ms} req_id={getattr(request, '_request_id', '-') }"
        )
        # Security headers
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-Frame-Options", "DENY")
    except Exception:
        pass
    return response


# Global error handler to standardize JSON errors


@app.errorhandler(Exception)
def _handle_error(e):
    req_id = getattr(request, "_request_id", None)
    # Application errors with structured details
    if isinstance(e, AppError):
        _logger.error(str(e))
        payload = {
            "error": e.__class__.__name__,
            "message": e.message,
            "code": e.code or "ERROR",
            "details": e.details,
            "request_id": req_id,
        }
        return payload, 500
    if isinstance(e, HTTPException):
        code = e.code or 500
        _logger.error(f"http_error status={code} path={request.path} msg={e}")
        return {"error": e.name, "message": str(e), "code": "ERROR", "request_id": req_id}, code
    _logger.exception(f"unhandled_error path={request.path}")
    return {"error": "Internal Server Error", "code": "ERROR", "request_id": req_id}, 500


@app.route("/")
def index():
    """Root endpoint for API server (no static files)."""
    return {
        "service": "robotdegilim-backend",
        "endpoints": ["/run-scrape", "/run-musts", "/status", "/speed"],
    }, 200


class RunScrape(Resource):
    def get(self):
        s3 = get_s3_client()
        # Reject if already busy
        current = get_status(s3)
        if current.get("status") == "busy":
            return {"status": "System is busy", "code": "BUSY"}, 503
        try:
            # Mark busy early
            set_busy(s3)
            # Run scrape (now purely functional w.r.t busy state)
            run_scrape()
            # Mark departments ready
            st = set_status(s3, depts_ready=True)

            # Run NTE processing after successful scrape
            try:
                run_nte()
            except Exception as e:
                _logger.error(f"NTE processing failed, error: {str(e)}")
                # Do not fail the whole scrape if NTE fails

            # If a musts run was queued during busy period, run it now
            if st.get("queued_musts"):
                _logger.info("musts run was queued; running after scrape completion (same busy window)")
                try:
                    run_musts()  # already busy from earlier
                    set_status(s3, queued_musts=False)
                    return {"status": "Scraping and NTE completed; musts completed successfully"}, 200
                except Exception as e:
                    _logger.error(f"queued musts run failed, error: {str(e)}")
                    return {"status": "Scraping and NTE completed; musts failed", "code": "ERROR"}, 500
            return {"status": "Scraping and NTE completed successfully"}, 200
        except Exception as e:
            _logger.error(str(e))
            return {"error": "Error running scrape process", "code": "ERROR"}, 500
        finally:
            try:
                # Always attempt to mark idle unless another request changed state
                set_idle(s3)
            except Exception as e:
                _logger.error(f"failed to set idle after scrape, error: {str(e)}")


class RunMusts(Resource):
    def get(self):
        s3 = get_s3_client()
        st = get_status(s3)
        # If departments data is not ready yet, queue and exit
        if not st.get("depts_ready"):
            if not st.get("queued_musts"):
                set_status(s3, queued_musts=True)
                return {
                    "status": "Departments data unavailable; musts queued to run after scrape",
                    "code": "QUEUED",
                }, 202
            return {
                "status": "Musts already queued; waiting for scrape to produce data",
                "code": "QUEUED",
            }, 202

        # If system currently busy (e.g., scrape in progress), queue
        if st.get("status") == "busy":
            if not st.get("queued_musts"):
                set_status(s3, queued_musts=True)
                return {
                    "status": "System busy; musts queued to run after scrape",
                    "code": "QUEUED",
                }, 202
            return {"status": "System busy; musts already queued", "code": "QUEUED"}, 202

        try:
            set_busy(s3)
            run_musts()
            set_status(s3, queued_musts=False)
            return {"status": "Get musts completed successfully", "code": "OK"}, 200
        except Exception as e:
            _logger.error(str(e))
            if app_constants.noDeptsErrMsg in str(e):
                set_status(s3, depts_ready=False, queued_musts=True)
                _logger.info("departments data missing; queued musts until after scrape")
                return {
                    "status": "Departments data missing; musts queued to run after next scrape",
                    "code": "QUEUED",
                }, 202
            return {"error": "Error running get musts process", "code": "ERROR"}, 500
        finally:
            try:
                set_idle(s3)
            except Exception as ie:
                _logger.error(f"failed to set idle after musts, error: {str(ie)}")


# Add API resources
api.add_resource(RunScrape, "/run-scrape")
api.add_resource(RunMusts, "/run-musts")


@app.route("/status")
def status():
    """Report backend readiness and S3 status.json busy/idle state."""
    try:
        s3 = get_s3_client()
        st = get_status(s3)
        return {
            "status": st.get("status"),
            "queued_musts": st.get("queued_musts"),
            "depts_ready": st.get("depts_ready"),
            "version": app_constants.app_version,
        }, 200
    except Exception as e:
        _logger.error(f"status check failed, error: {str(e)}")
        return {"status": "unknown", "error": "status check failed"}, 500

@app.route("/speed", methods=["GET", "POST"])
def speed():
    """Get or set throttling speed mode: fast | slow | normal.

    GET: returns current mode and scale.
    POST: accepts ONLY a JSON body: {"mode": "<value>"}
    """
    if request.method == "POST":
        if not request.is_json:
            return {"ok": False, "error": "JSON body required"}, 400
        data = request.get_json(silent=True) or {}
        mode = data.get("mode")
        if mode is None:
            return {"ok": False, "error": "Missing 'mode' in JSON body"}, 400
        try:
            state = set_speed_mode(mode)
        except ValueError as ve:
            return {"ok": False, "error": str(ve)}, 400
        except Exception as e:
            _logger.error(f"speed toggle failed, error: {str(e)}")
            return {"ok": False, "error": "speed toggle failed"}, 500
        return {"ok": True, **state}, 200

    # GET
    return get_speed_mode(), 200


# For local debugging, uncomment the below lines
"""
if __name__ == "__main__":
    app.run(host="localhost", port=8000)
"""