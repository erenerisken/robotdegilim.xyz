from pydantic import BaseModel, Field

from app.core.settings import get_settings
from app.core.constants import RequestType

def _build_root_payload() -> dict:
    settings=get_settings()
    return {
        "app_name": settings.APP_NAME,
        "admin_email": settings.ADMIN_EMAIL,
        "description": settings.APP_DESCRIPTION,
        "version": settings.APP_VERSION,
        "endpoints": {
            "root": {
                "path": "/",
                "description": "Root endpoint providing basic information about the API",
            },
            "scrape": {
                "path": "/run-scrape",
                "description": "Endpoint to trigger the scraping process",
            },
        },
    }

class RootResponse(BaseModel):
    root: dict = Field(default_factory=_build_root_payload)

class ResponseModel(BaseModel):
    request_type: str
    status: str
    message: str
    extra:dict | None = None