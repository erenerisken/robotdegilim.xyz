import json
import logging
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
from pathlib import Path

from app.core.settings import get_settings, get_path


def _build_formatter():
    settings = get_settings()
    if settings.LOG_JSON:
        return _JsonFormatter()
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    return logging.Formatter(fmt)


def setup_logging():
    settings = get_settings()

    log_dir = get_path("LOG_DIR")
    log_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    app_logger = logging.getLogger("app")
    scrape_logger = logging.getLogger("scrape")
    error_logger = logging.getLogger("error")

    for lg in (app_logger, scrape_logger, error_logger):
        lg.setLevel(level)

    formatter = _build_formatter()

    app_file = log_dir / "app.log"
    jobs_file = log_dir / "jobs.log"
    err_file = log_dir / "error.log"

    _add_handler(app_logger, app_file, formatter, level)
    _add_handler(scrape_logger, jobs_file, formatter, level)
    _add_handler(error_logger, err_file, formatter, logging.ERROR)

    if settings.LOG_CONSOLE:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)
        app_logger.addHandler(console)
        scrape_logger.addHandler(console)
        error_logger.addHandler(console)

    _add_email_handler(error_logger)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _add_handler(logger: logging.Logger, path: Path, formatter: logging.Formatter, level: int):
    handler = TimedRotatingFileHandler(
        path,
        when="midnight",
        interval=1,
        backupCount=get_settings().LOG_RETENTION_DAYS,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _add_email_handler(error_logger: logging.Logger) -> None:
    settings = get_settings()
    if not settings.MAIL_ENABLED:
        return
    if not settings.MAIL_SERVER or not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        return
    if not settings.MAIL_RECIPIENT:
        return

    sender = settings.MAIL_SENDER or settings.MAIL_USERNAME
    subject = f"{settings.MAIL_SUBJECT_PREFIX} error"

    handler = SMTPHandler(
        mailhost=(settings.MAIL_SERVER, settings.MAIL_PORT),
        fromaddr=sender,
        toaddrs=[settings.MAIL_RECIPIENT],
        subject=subject,
        credentials=(settings.MAIL_USERNAME, settings.MAIL_PASSWORD),
        secure=(),
    )
    handler.setLevel(logging.ERROR)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    error_logger.addHandler(handler)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        return json.dumps(payload, ensure_ascii=False)
