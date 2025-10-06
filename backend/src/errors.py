"""Application-specific error types with structured payloads."""

from __future__ import annotations

from typing import Any, Optional


class AppError(Exception):
    """Base error that captures a message, code, and optional details."""

    message: str
    code: Optional[str]
    details: Any

    def __init__(self, message: str = "", *, code: str | None = None, details: Any | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

    def __str__(self) -> str:  # pragma: no cover - trivial override
        return self.message or super().__str__()


class StatusError(AppError):
    """Marker subclass of AppError for recoverable failures."""

    pass

class NetworkError(AppError):
    """Marker subclass of AppError for network-related failures."""
    pass

class S3Error(NetworkError):
    """Marker subclass of NetworkError for S3 publishing failures."""
    pass

class AbortMustsError(AppError):
    """Marker subclass of AppError to abort musts fetching."""
    pass

class AbortScrapingError(AppError):
    """Marker subclass of AppError to abort scraping."""
    pass

class AbortNteAvailableError(AppError):
    """Marker subclass of AppError to abort NTE processing."""
    pass
class AbortNteListError(AppError):
    """Marker subclass of AppError to abort NTE list fetching."""
    pass

class IOError(AppError):
    """Marker subclass of AppError for I/O-related failures."""
    pass