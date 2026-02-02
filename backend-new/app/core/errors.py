from __future__ import annotations

from dataclasses import dataclass
import traceback
from typing import Optional


@dataclass
class AppError(Exception):
    message: str
    code: Optional[str] = None
    context: Optional[dict] = None
    cause: Optional[Exception] = None
    call_stack: Optional[str] = None
    traceback_exists: bool = False

    def __post_init__(self) -> None:
        cause_tb = getattr(self.cause, "__traceback__", None) if self.cause else None
        self_tb = getattr(self, "__traceback__", None)
        self.traceback_exists = bool(cause_tb or self_tb)
        if not self.traceback_exists and self.call_stack is None:
            self.call_stack = "".join(traceback.format_stack()[:-1])

    def __str__(self) -> str:
        return self.message

    def to_log(self) -> dict:
        payload = {"message": self.message}
        if self.code:
            payload["code"] = self.code
        if self.context:
            payload["context"] = self.context
        if self.cause:
            payload["cause"] = str(self.cause)
        if self.traceback_exists:
            payload["traceback_exists"] = True
        elif self.call_stack:
            payload["stack"] = self.call_stack
        return payload
