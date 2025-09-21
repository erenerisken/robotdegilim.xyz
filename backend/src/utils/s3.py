import json
import logging
import os
from typing import Dict, Optional

import boto3

from src.config import app_constants
from src.errors import RecoverError
import time
import random

# Internal module-level cache for the S3 client. We avoid @lru_cache so we can
# expose an explicit reset hook (useful for tests / credential rotation).
_S3_CLIENT: Optional[boto3.client] = None


logger = logging.getLogger(app_constants.log_utils)


def get_s3_client(*, refresh: bool = False) -> boto3.client:
    """Return a cached boto3 S3 client.

    If ACCESS_KEY / SECRET_ACCESS_KEY (or standard AWS var names) are present at the
    time of first call they are used; otherwise the default credential chain is
    relied upon. Pass refresh=True to force recreation (e.g., after rotating
    credentials in the environment).
    """
    global _S3_CLIENT
    if _S3_CLIENT is not None and not refresh:
        return _S3_CLIENT
    try:
        # Prefer explicit custom names, then fall back to standard AWS names.
        access = app_constants.aws_access_key_id
        secret = app_constants.aws_secret_access_key
        kwargs = {}
        if access and secret:
            kwargs = {
                "aws_access_key_id": access,
                "aws_secret_access_key": secret,
            }
        _S3_CLIENT = boto3.client("s3", **kwargs)
        return _S3_CLIENT
    except Exception as e:
        logger.error(f"failed to create s3 client, error: {str(e)}")
        raise e


def reset_s3_client():
    """Clear the cached S3 client (used in tests or after credential rotation)."""
    global _S3_CLIENT
    _S3_CLIENT = None


def upload_to_s3(file_path: str, s3_key: str, retries: int = 5):
    """Uploads a file to the S3 bucket and makes it public, with retries."""
    attempt = 0
    last_error = None
    s3_client = get_s3_client()
    while attempt <= retries:
        try:
            s3_client.upload_file(
                file_path,
                app_constants.s3_bucket_name,
                s3_key,
                ExtraArgs={"ACL": "public-read"},
            )
            return
        except Exception as e:
            last_error = e
            if attempt == retries:
                break
            delay = min(10, (2**attempt) + random.uniform(0, 0.5))
            time.sleep(delay)
            attempt += 1
    raise RecoverError(
        f"Failed to upload to S3: path: {file_path}, error: {str(last_error)}"
    )


def is_idle() -> bool:
    """Fetches status.json from S3 and checks if the backend is idle."""
    try:
        s3_client = get_s3_client()
        response = s3_client.get_object(
            Bucket=app_constants.s3_bucket_name, Key=app_constants.status_json
        )
        status_data = response["Body"].read().decode("utf-8")
        status_json: Dict[str, str] = json.loads(status_data)
        return status_json.get("status") == "idle"
    except Exception as e:
        logger.error(f"Error fetching or reading status.json, error: {str(e)}")
        return False
