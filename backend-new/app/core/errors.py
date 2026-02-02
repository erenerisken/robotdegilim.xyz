"""Application-level error model with consistent structured logging support."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import traceback
from typing import Any


@dataclass
class AppError(Exception):
    """Base application error carrying message, code, context, and optional cause."""

    message: str
    code: str | None = None
    context: dict[str, Any] | None = None
    cause: Exception | None = None
    call_stack: str | None = None

    def __post_init__(self) -> None:
        """Capture call stack when the error object is created."""
        if self.call_stack is None:
            self.call_stack = "".join(traceback.format_stack()[:-1])

    def __str__(self) -> str:
        return self.message

    def _exc_info(self) -> tuple[type[BaseException], BaseException, Any] | None:
        """Return traceback-bearing exception info tuple when available."""
        if self.cause and getattr(self.cause, "__traceback__", None):
            return (type(self.cause), self.cause, self.cause.__traceback__)
        if getattr(self, "__traceback__", None):
            return (type(self), self, self.__traceback__)
        return None

    def to_log(self, *, include_stack: bool = False) -> dict[str, Any]:
        """Build structured log payload for this error."""
        payload = {"message": self.message}
        if self.code:
            payload["code"] = self.code
        if self.context:
            payload["context"] = self.context
        if self.cause:
            payload["cause"] = str(self.cause)
        if include_stack and self.call_stack:
            payload["stack"] = self.call_stack
        return payload

    def log(self, logger: logging.Logger, level: int) -> None:
        """Log this error with optional traceback or fallback stack information."""
        exc_info = self._exc_info() if level >= logging.ERROR else None
        payload = self.to_log(include_stack=(exc_info is None and level >= logging.ERROR))
        logger.log(level, json.dumps(payload, ensure_ascii=False, indent=2), exc_info=exc_info)
