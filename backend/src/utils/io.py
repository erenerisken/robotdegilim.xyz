import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Union

from src.config import app_constants
from src.utils.s3 import get_s3_client

def load_json_local_then_s3(
    local_path: PathLike,
    s3_key: str,
    *,
    label: str,
    logger: logging.Logger,
) -> Dict[str, Any]:
    """Load a JSON dict from local path first, then fall back to S3 by key.

    - local_path: filesystem path to try first (str or Path)
    - s3_key: object key in the configured S3 bucket
    - label: short human-readable label used in logs (e.g., "departments")
    - logger: module/component logger to emit messages to

    Returns an empty dict on any failure or if the parsed JSON is not a dict.
    """
    # 1) Prefer local cache if present
    path = Path(local_path) if not isinstance(local_path, Path) else local_path
    data = load_json_safe(path)
    if data:
        logger.info(
            f"{label} loaded (local): count={len(data)} file={os.path.basename(str(path))}"
        )
        return data

    # 2) Fallback to S3
    try:
        s3 = get_s3_client()
        obj = s3.get_object(Bucket=app_constants.s3_bucket_name, Key=s3_key)
        body = obj["Body"].read().decode("utf-8")
        data = json.loads(body)
        if isinstance(data, dict) and data:
            logger.info(
                f"{label} loaded (s3): count={len(data)} key={s3_key}"
            )
            return data
    except Exception as e:
        logger.warning(f"could not load {label} from S3, error: {str(e)}")
    return {}
