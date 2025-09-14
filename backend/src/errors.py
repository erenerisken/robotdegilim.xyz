import inspect
from typing import Optional, Dict, Any, Mapping, Iterable
import json
import textwrap

__all__ = ["RecoverError", "AppError"]


# -------- helpers --------

def _caller_name(default: str = "<unknown>") -> str:
    """Return immediate caller function name with minimal overhead."""
    try:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            return frame.f_back.f_code.co_name  # type: ignore[return-value]
    except Exception:
        pass
    return default


def _json_coerce(obj: Any) -> Any:
    """Best-effort conversion of values to JSON-safe types."""
    try:
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj
        if isinstance(obj, Mapping):
            return {str(k): _json_coerce(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [_json_coerce(v) for v in list(obj)]
        return str(obj)
    except Exception:
        return str(obj)

# -------- base and recoverable errors --------

class AppError(Exception):
    """Base application error with structured payload utilities."""

    def __init__(self, message: str, details: Optional[Mapping[str, Any]] = None, code: Optional[str] = None) -> None:
        self.message = message
        self.code = code
        tmp = dict(details) if details else {}
        if "function" not in tmp:
            tmp["function"] = _caller_name()
        self.details: Dict[str, Any] = tmp
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        details = _json_coerce(self.details)
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": details,
        }

    def __str__(self) -> str:  # pragma: no cover
        base = f"[{self.code}] {self.message}" if self.code else self.message
        if self.details:
            return f"{base} | Details: {self._format_details()}"
        return base

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r}, details={self.details!r})"

    def _format_details(self, max_len: int = 2000) -> str:
        """Pretty JSON for text logs with truncation."""
        try:
            text = json.dumps(self.to_dict().get("details", {}), ensure_ascii=False, sort_keys=True, indent=2, default=str)
        except Exception:
            # Fallback conservative formatting
            text = str(self.details)
        if len(text) > max_len:
            text = text[: max_len - 12] + "... <truncated>"
        # Indent multiline for readability when embedded
        return textwrap.indent(text, "\t").lstrip("\t")


class RecoverError(AppError):
    """Recoverable application error for graceful unwind without partial state."""
    pass
