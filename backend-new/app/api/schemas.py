from pydantic import BaseModel, PrivateAttr
from app.core.settings import get_setting

class ErrorResponse(BaseModel):
    message: str
    info: dict = {}


class RootResponse(BaseModel):
    _app_name:str = PrivateAttr(get_setting("APP_NAME", "https://robotdegilim.xyz backend"))
    _admin_email:str = PrivateAttr(get_setting("ADMIN_EMAIL", "info.robotdegilim@gmail.com"))
    _app_description:str = PrivateAttr(get_setting("APP_DESCRIPTION", "Backend API for https://robotdegilim.xyz"))
    _app_version:str = PrivateAttr(get_setting("APP_VERSION", "1.0.0"))
    root:dict = {
        "app_name": _app_name,
        "admin_email": _admin_email,
        "description": _app_description,
        "version": _app_version,
        "endpoints": {
            "root": {
                "path": "/",
                "description": "Root endpoint providing basic information about the API"
            },
            "scrape": {
                "path": "/run-scrape",
                "description": "Endpoint to trigger the scraping process"
            }
        }
    }

class ScrapeResponse(BaseModel):
    status: str
    data: dict
