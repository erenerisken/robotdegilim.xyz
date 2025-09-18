from typing import Optional, Mapping, Any

__all__ = ["RecoverError", "AppError"]


class AppError(Exception):
    """Minimal application error used only for typing/catching."""
    
    pass


class RecoverError(AppError):
    """Marker subclass of AppError for recoverable failures."""

    pass
