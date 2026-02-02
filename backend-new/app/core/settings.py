"""Application settings and helper accessors."""

from functools import lru_cache
from pathlib import Path
import uuid
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


def _default_headers_factory() -> dict[str, str]:
    """Build default HTTP headers for outbound scrape requests."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.7632.27 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr-TR,tr;q=0.8",
    }


class Settings(BaseSettings):
    """Typed settings model loaded from environment variables."""

    # Application settings
    APP_NAME: str = "https://robotdegilim.xyz backend"
    APP_DESCRIPTION: str = "Backend API for https://robotdegilim.xyz"
    ADMIN_EMAIL: str = "info.robotdegilim@gmail.com"
    APP_VERSION: str = "1.0.0"
    # S3 Settings
    S3_LOCK_OWNER_ID: str = Field(default_factory=lambda: str(uuid.uuid4()))
    S3_LOCK_TIMEOUT_SECONDS: int = 3 * 60 * 60  # 3 hours
    # HTTP settings
    HTTP_TIMEOUT: int = 15
    GLOBAL_RETRIES: int = 5
    RETRY_BASE_DELAY: float = 1.0
    RETRY_JITTER: float = 0.25
    DEFAULT_HEADERS: dict[str, str] = Field(default_factory=_default_headers_factory)
    THROTTLE_ENABLED: bool = False
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    LOG_CONSOLE: bool = True
    LOG_DIR: str = "data/logs"
    LOG_RETENTION_DAYS: int = 7
    TIMEZONE: str = "Europe/Istanbul"
    # Mail logging settings
    MAIL_ENABLED: bool = False
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_SENDER: str = ""
    MAIL_RECIPIENT: str = ""
    MAIL_SUBJECT_PREFIX: str = "[robotdegilim]"
    # Paths
    DATA_DIR: str = "data"
    # Scrape process settings
    SCRAPE_PARSER_VERSION: str = "1.0.0"


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    settings = Settings()
    if not settings.MAIL_SENDER:
        settings.MAIL_SENDER = settings.MAIL_USERNAME
    if not settings.MAIL_RECIPIENT:
        settings.MAIL_RECIPIENT = settings.ADMIN_EMAIL
    return settings


def get_setting(name: str, default: Any = None) -> Any:
    """Return a single setting by attribute name."""
    settings = get_settings()
    return getattr(settings, name, default)


def get_path(name: str, default: Any = None) -> Path | None:
    """Return a setting as a Path when present."""
    value = get_setting(name, default)
    return Path(value) if value is not None else None
