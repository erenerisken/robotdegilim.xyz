import logging
import json as _json
from typing import Optional, Callable


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter.

    Optionally accepts a time converter (like a TZ-aware converter) to align
    timestamps with the app's configured timezone.
    """

    def __init__(
        self, datefmt: Optional[str] = "%Y-%m-%dT%H:%M:%S%z", converter: Optional[Callable] = None
    ):
        super().__init__()
        self._datefmt = datefmt
        if converter is not None:
            # logging.Formatter reads 'converter' attribute to compute asctime
            self.converter = converter  # type: ignore[attr-defined]

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, datefmt=self._datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        rid = getattr(record, "request_id", None)
        if rid:
            payload["request_id"] = rid
        return _json.dumps(payload, ensure_ascii=False)
