from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "https://robotdegilim.xyz backend"
    APP_DESCRIPTION: str = "Backend API for https://robotdegilim.xyz"
    ADMIN_EMAIL: str = "info.robotdegilim@gmail.com"
    APP_VERSION: str = "1.0.0"

    S3_LOCK_TIMEOUT_SECONDS: int = 300  # 5 minutes

@lru_cache()
def get_settings():
    return Settings()

def get_setting(name: str, default=None):
    settings = get_settings()
    return getattr(settings, name, default)