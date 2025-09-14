import json
import logging
import os
from typing import Dict, Any

from config import app_constants
from errors import RecoverError


logger = logging.getLogger(app_constants.log_scrape)


def write_json(data: dict, file_path: str) -> None:
    """Write a JSON object to the given path with UTF-8 and indentation."""
    try:
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        raise RecoverError("Failed to write json", {"file_path": file_path, "error": str(e)}) from None


def _load_json_safe(file_path: str) -> Dict[str, Any]:
    """Load JSON dict from a file, returning {} on any failure."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.error(f"Failed to read json file {file_path}: {e}")
        return {}


def _norm_code(code: Any) -> str:
    return str(code).strip().upper()


def _norm_prefix(p: Any) -> str:
    return str(p or "").strip()


def _load_prefix_map(file_path: str, label: str) -> Dict[str, str]:
    """Internal helper to load a prefix map from a JSON file with entries { code: { 'p': prefix } }.

    - Normalizes codes to uppercase, strips whitespace
    - Skips missing/empty prefixes
    - Logs a one-line summary with kept/skipped counts
    """
    data = _load_json_safe(file_path)
    total = len(data)
    kept = 0
    result: Dict[str, str] = {}
    for raw_code, entry in data.items():
        try:
            prefix = _norm_prefix((entry or {}).get("p", ""))
            if not prefix:
                continue
            code = _norm_code(raw_code)
            result[code] = prefix
            kept += 1
        except Exception:
            continue
    if total:
        logger.info(f"{label} prefixes loaded from {os.path.basename(str(file_path))}: kept={kept} skipped={total - kept}")
    return result


def load_prefixes() -> Dict[str, str]:
    """Load department prefixes from departments.json.

    Returns a mapping of DEPT_CODE -> PREFIX. Skips entries without a valid 'p'.
    """
    file_path = app_constants.data_dir / app_constants.departments_json
    return _load_prefix_map(str(file_path), label="departments")


def load_manual_prefixes() -> Dict[str, str]:
    """Load department prefixes from manualPrefixes.json.

    Returns a mapping of DEPT_CODE -> PREFIX. Skips entries without a valid 'p'.
    """
    file_path = app_constants.data_dir / app_constants.manual_prefixes_json
    return _load_prefix_map(str(file_path), label="manual")


def load_prefixes_combined() -> Dict[str, str]:
    """Load prefixes and apply manual overrides. Returns merged mapping."""
    base = load_prefixes()
    overrides = load_manual_prefixes()
    base.update(overrides)
    logger.info(f"combined prefixes: total={len(base)} (overrides={len(overrides)})")
    return base
