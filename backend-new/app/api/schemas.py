from pydantic import BaseModel, Field

from app.core.settings import get_setting
from app.core.constants import RequestType

def _build_root_payload() -> dict:
    return {
        "app_name": get_setting("APP_NAME", "https://robotdegilim.xyz backend"),
        "admin_email": get_setting("ADMIN_EMAIL", "info.robotdegilim@gmail.com"),
        "description": get_setting("APP_DESCRIPTION", "Backend API for https://robotdegilim.xyz"),
        "version": get_setting("APP_VERSION", "1.0.0"),
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
    request_type: RequestType
    status: str
    messsage: str
    extra:dict | None = None