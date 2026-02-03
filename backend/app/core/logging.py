"""Centralized logging setup and helper utilities for the application."""

import json
import logging
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
from pathlib import Path
from typing import Any

from app.core.constants import (
    LOG_FILE_APP,
    LOG_FILE_ERROR,
    LOG_FILE_MUSTS,
    LOG_FILE_NTE_LIST,
    LOG_FILE_SCRAPE,
    LOGGER_APP,
    LOGGER_ERROR,
    LOGGER_MUSTS,
    LOGGER_NTE_LIST,
    LOGGER_SCRAPE,
)
from app.core.errors import AppError
from app.core.paths import log_dir
from app.core.settings import get_settings

_LOGGER_NAMES: tuple[str, ...] = (
    LOGGER_APP,
    LOGGER_SCRAPE,
    LOGGER_MUSTS,
    LOGGER_NTE_LIST,
    LOGGER_ERROR,
)


def _build_formatter() -> logging.Formatter:
    """Build the configured formatter (plain text or JSON)."""
    settings = get_settings()
    if settings.LOG_JSON:
        return _JsonFormatter()
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    return logging.Formatter(fmt)


def log_item(
    logger_name: str,
    level: int,
    log: Any,
    *,
    exc_info: Any = None,
    stack_info: bool = False,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log an item to a named logger with unified AppError support."""
    if logger_name not in _LOGGER_NAMES:
        logger_name = LOGGER_APP
    logger = logging.getLogger(logger_name)
    if isinstance(log, AppError):
        log.log(logger, level)
    else:
        try:
            logger.log(level, str(log), exc_info=exc_info, stack_info=stack_info, extra=extra)
        except Exception as e:
            err = e if isinstance(e, AppError) else AppError("Logging failed", "LOGGING_FAILED", cause=e)
            raise err


def setup_logging() -> None:
    """Configure app, scrape, and error loggers with file/console/mail handlers."""
    settings = get_settings()

    log_dir_path = log_dir()
    log_dir_path.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    app_logger = logging.getLogger(LOGGER_APP)
    scrape_logger = logging.getLogger(LOGGER_SCRAPE)
    musts_logger = logging.getLogger(LOGGER_MUSTS)
    nte_list_logger = logging.getLogger(LOGGER_NTE_LIST)
    error_logger = logging.getLogger(LOGGER_ERROR)

    for lg in (app_logger, scrape_logger, musts_logger, nte_list_logger, error_logger):
        lg.setLevel(level)
        lg.handlers.clear()
        lg.propagate = False

    formatter = _build_formatter()

    app_file = log_dir_path / LOG_FILE_APP
    scrape_file = log_dir_path / LOG_FILE_SCRAPE
    musts_file = log_dir_path / LOG_FILE_MUSTS
    nte_list_file = log_dir_path / LOG_FILE_NTE_LIST
    err_file = log_dir_path / LOG_FILE_ERROR

    _add_handler(app_logger, app_file, formatter, level)
    _add_handler(scrape_logger, scrape_file, formatter, level)
    _add_handler(musts_logger, musts_file, formatter, level)
    _add_handler(nte_list_logger, nte_list_file, formatter, level)
    _add_handler(error_logger, err_file, formatter, logging.ERROR)

    if settings.LOG_CONSOLE:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)
        app_logger.addHandler(console)
        scrape_logger.addHandler(console)
        musts_logger.addHandler(console)
        nte_list_logger.addHandler(console)
        error_logger.addHandler(console)

    _add_email_handler(error_logger)


def _add_handler(logger: logging.Logger, path: Path, formatter: logging.Formatter, level: int) -> None:
    """Add a timed rotating file handler to a logger."""
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
    """Minimal JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        return json.dumps(payload, ensure_ascii=False)
