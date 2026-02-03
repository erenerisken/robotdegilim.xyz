"""Pydantic schemas used by API routes and service responses."""

from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import RequestType
from app.core.settings import get_settings


def _build_root_payload() -> dict:
    """Build the root endpoint payload from application settings."""
    settings = get_settings()
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
            "musts": {
                "path": "/run-musts",
                "description": "Endpoint to trigger the musts processing workflow",
            },
        },
    }


class RootResponse(BaseModel):
    """Response model for the root endpoint."""

    root: dict = Field(default_factory=_build_root_payload)


class ResponseModel(BaseModel):
    """Common response model returned by request handlers."""

    request_type: RequestType
    status: str
    message: str
    extra: dict[str, Any] | None = None
