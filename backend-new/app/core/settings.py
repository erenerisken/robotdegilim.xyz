from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "https://robotdegilim.xyz backend"
    APP_DESCRIPTION: str = "Backend API for https://robotdegilim.xyz"
    ADMIN_EMAIL: str = "info.robotdegilim@gmail.com"
    APP_VERSION: str = "1.0.0"

    S3_LOCK_TIMEOUT_SECONDS: int = 300  # 5 minutes

    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    LOG_CONSOLE: bool = True
    LOG_DIR: str = "data/logs"
    LOG_RETENTION_DAYS: int = 7
    TIMEZONE: str = "Europe/Istanbul"

    MAIL_ENABLED: bool = False
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_SENDER: str = ""
    MAIL_RECIPIENT: str = ""
    MAIL_SUBJECT_PREFIX: str = "[robotdegilim]"

@lru_cache()
def get_settings():
    settings = Settings()
    if not settings.MAIL_SENDER:
        settings.MAIL_SENDER = settings.MAIL_USERNAME
    if not settings.MAIL_RECIPIENT:
        settings.MAIL_RECIPIENT = settings.ADMIN_EMAIL
    return settings

def get_setting(name: str, default=None):
    settings = get_settings()
    return getattr(settings, name, default)
