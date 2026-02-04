"""Admin helpers for reading/updating runtime settings."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from app.core.settings import Settings, get_settings

_BLOCKED_SETTING_KEYS: set[str] = {
    "ADMIN_SECRET",
    "MAIL_PASSWORD",
    "MAIL_USERNAME",
    "S3_LOCK_OWNER_ID",
}
_MASKED_SETTING_KEYS: set[str] = {
    "ADMIN_SECRET",
    "MAIL_PASSWORD",
    "MAIL_USERNAME",
    "S3_LOCK_OWNER_ID",
}
_ENV_KEY_PATTERN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def get_public_settings() -> dict[str, Any]:
    """Return current settings with sensitive values masked."""
    settings = get_settings()
    dumped = settings.model_dump()
    public: dict[str, Any] = {}
    for key, value in dumped.items():
        public[key] = "***" if key in _MASKED_SETTING_KEYS else value
    return public


def apply_settings_updates(updates: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], int, int]:
    """Apply settings updates into backend/.env and reload settings cache.

    Returns:
        tuple[results, applied_count, failed_count]
    """
    results: dict[str, dict[str, Any]] = {}
    if not updates:
        return results, 0, 0

    valid_env_updates: dict[str, str] = {}

    for key, raw_value in updates.items():
        if key not in Settings.model_fields:
            results[key] = {"ok": False, "message": "unknown setting key"}
            continue
        if key in _BLOCKED_SETTING_KEYS:
            results[key] = {"ok": False, "message": "blocked key"}
            continue
        try:
            validated = Settings(**{key: raw_value})
            normalized_value = getattr(validated, key)
            valid_env_updates[key] = _encode_env_value(normalized_value)
            results[key] = {"ok": True, "message": "updated"}
        except Exception:
            results[key] = {"ok": False, "message": "invalid value"}

    if valid_env_updates:
        env_path = _settings_env_path()
        _update_env_file(env_path, valid_env_updates)
        get_settings.cache_clear()
        get_settings()

    applied_count = sum(1 for row in results.values() if row.get("ok"))
    failed_count = len(results) - applied_count
    return results, applied_count, failed_count


def _settings_env_path() -> Path:
    """Return backend settings .env path."""
    return Path(__file__).resolve().parents[2] / ".env"


def _encode_env_value(value: Any) -> str:
    """Encode a Python value into .env-friendly representation."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)

    text = str(value)
    if any(ch in text for ch in (" ", "#", '"', "'")):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f"\"{escaped}\""
    return text


def _update_env_file(path: Path, updates: dict[str, str]) -> None:
    """Update only targeted keys in .env while preserving unrelated lines/comments."""
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    key_to_line: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = _ENV_KEY_PATTERN.match(line)
        if not match:
            continue
        key_to_line[match.group(1)] = index

    for key, value in updates.items():
        line = f"{key}={value}"
        if key in key_to_line:
            lines[key_to_line[key]] = line
        else:
            lines.append(line)

    text = "\n".join(lines) + ("\n" if lines else "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
