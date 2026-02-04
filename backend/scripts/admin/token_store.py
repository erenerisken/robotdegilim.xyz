"""Token file helpers for admin lock token persistence."""

from __future__ import annotations

from .config import TOKEN_FILE_PATH


def load_token() -> str | None:
    """Read lock token from token file if present and non-empty."""
    if not TOKEN_FILE_PATH.exists():
        return None
    token = TOKEN_FILE_PATH.read_text(encoding="utf-8").strip()
    return token or None


def save_token(token: str) -> None:
    """Persist lock token to token file."""
    TOKEN_FILE_PATH.write_text(token.strip(), encoding="utf-8")


def clear_token() -> None:
    """Delete token file when present."""
    TOKEN_FILE_PATH.unlink(missing_ok=True)
