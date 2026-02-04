"""Admin authentication helpers."""

import hmac

from app.core.errors import AppError
from app.core.settings import get_settings


def verify_admin_secret(provided_secret: str | None) -> None:
    """Validate incoming admin secret header against configured secret."""
    settings = get_settings()
    configured_secret = settings.ADMIN_SECRET

    if not configured_secret:
        raise AppError("Admin secret is not configured.", "ADMIN_SECRET_NOT_CONFIGURED")
    if not provided_secret:
        raise AppError("Missing admin secret.", "ADMIN_AUTH_FAILED")
    if not hmac.compare_digest(provided_secret, configured_secret):
        raise AppError("Invalid admin secret.", "ADMIN_AUTH_FAILED")
