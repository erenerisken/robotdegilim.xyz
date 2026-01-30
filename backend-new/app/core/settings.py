from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "https://robotdegilim.xyz backend"
    admin_email: str = "info.robotdegilim@gmail.com"

    s3_lock_timeout_seconds: int = 300  # 5 minutes

@lru_cache()
def get_settings():
    return Settings()

def get_setting(name: str, default=None):
    settings = get_settings()
    return getattr(settings, name, default)