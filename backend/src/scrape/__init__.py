__all__ = []

from typing import Any

def _strip_upper(s: Any) -> str:
    return str(s or "").strip().upper()