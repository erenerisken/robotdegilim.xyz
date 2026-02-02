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
    traceback_info: Optional[str] = None

    def __post_init__(self) -> None:
        if self.call_stack is None:
            self.call_stack = "".join(traceback.format_stack()[:-1])
        if self.traceback_info is None:
            tb = None
            if self.cause and getattr(self.cause, "__traceback__", None):
                tb = self.cause.__traceback__
            elif getattr(self, "__traceback__", None):
                tb = self.__traceback__
            if tb is not None:
                self.traceback_info = "".join(
                    traceback.format_exception(type(self.cause) if self.cause else type(self), self.cause or self, tb)
                )

    def __str__(self) -> str:
        return self.message

    def to_log(self) -> str:
        payload = {"message": self.message}
        if self.code:
            payload["code"] = self.code
        if self.context:
            payload["context"] = self.context
        if self.cause:
            payload["cause"] = str(self.cause)
        if self.traceback_info:
            payload["traceback"] = self.traceback_info
        if self.call_stack:
            payload["stack"] = self.call_stack
        return str(payload)
