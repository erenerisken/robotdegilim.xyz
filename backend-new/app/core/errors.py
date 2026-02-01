from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import Any, Optional


@dataclass
class AppError(Exception):
    message: str
    code: Optional[str] = None
    context: dict = field(default_factory=dict)
    cause: Optional[Exception] = None

    def __post_init__(self) -> None:
        # Capture the caller function where the error was created.
        if "caller" not in self.context:
            try:
                frame = inspect.stack()[2]
                self.context["caller"] = frame.function
            except Exception:
                self.context["caller"] = "unknown"

    def __str__(self) -> str:
        return self.message

    def to_log(self) -> dict:
        payload = {
            "message": self.message,
            "code": self.code,
            "context": self.context,
            "type": self.__class__.__name__,
        }
        if self.cause:
            payload["cause"] = str(self.cause)
        return payload


class NetworkError(AppError):
    pass


class ScrapeError(AppError):
    pass


class StorageError(AppError):
    pass


class ConfigError(AppError):
    pass


class ValidationError(AppError):
    pass
