"""Pydantic schemas used by API routes and service responses."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import AdminAction, RequestType
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
            "admin": {
                "path": "/admin",
                "description": "Admin control endpoint for lock/context/settings actions",
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

# Admin endpoint schemas

class AdminRequest(BaseModel):
    """Request model for admin endpoint action dispatch."""

    model_config = ConfigDict(extra="ignore")

    action: AdminAction
    payload: dict[str, Any] | None = None


class AdminKeyResult(BaseModel):
    """Per-key result model for settings_set updates."""

    ok: bool
    message: str


class AdminResponse(BaseModel):
    """Unified response envelope for /admin actions."""

    action: AdminAction
    status: str
    message: str
    data: dict[str, Any] | None = None
