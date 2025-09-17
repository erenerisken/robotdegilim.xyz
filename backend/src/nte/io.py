import json
from pathlib import Path
from typing import List, Dict, Any

from src.config import app_constants
from src.errors import RecoverError


def write_nte_available(nte_data: List[Dict[str, Any]]) -> Path:
    """Write NTE available courses to JSON file and return path."""
    # Ensure directory exists
    app_constants.data_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = app_constants.data_dir / app_constants.nte_available_json
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(nte_data, f, ensure_ascii=False, indent=4)
        return output_path
    except Exception as e:
        raise RecoverError(
            "Failed to write NTE available courses",
            {"path": str(output_path), "error": str(e)}
        ) from e 