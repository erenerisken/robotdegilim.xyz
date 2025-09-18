import logging
import os
from typing import Dict

from src.config import app_constants
from src.scrape.parse import _strip_upper
from src.utils.io import load_json_safe


logger = logging.getLogger(app_constants.log_scrape)


def _load_prefix_map(file_path: str, label: str) -> Dict[str, str]:
    """Internal helper to load a prefix map from a JSON file with entries { code: { 'p': prefix } }.

    - Normalizes codes to uppercase, strips whitespace
    - Skips missing/empty prefixes
    - Logs a one-line summary with kept/skipped counts
    """
    data = load_json_safe(file_path)
    total = len(data)
    kept = 0
    result: Dict[str, str] = {}
    for raw_code, entry in data.items():
        try:
            prefix = _strip_upper((entry or {}).get("p", ""))
            if not prefix:
                continue
            code = _strip_upper(raw_code)
            result[code] = prefix
            kept += 1
        except Exception:
            continue
    if total:
        logger.info(
            f"{label} prefixes loaded from {os.path.basename(str(file_path))}: kept={kept} skipped={total - kept}"
        )
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
    if not os.path.exists(file_path):
        logger.warning(
            "manualPrefixes.json not found at %s; proceeding without manual overrides",
            str(file_path),
        )
        return {}
    return _load_prefix_map(str(file_path), label="manual")


def load_prefixes_combined() -> Dict[str, str]:
    """Load prefixes and apply manual overrides. Returns merged mapping."""
    base = load_prefixes()
    overrides = load_manual_prefixes()
    base.update(overrides)
    logger.info(f"combined prefixes: total={len(base)} (overrides={len(overrides)})")
    return base
