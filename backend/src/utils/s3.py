import json
import logging
from typing import Dict

import boto3

from src.config import app_constants
from src.errors import RecoverError
import time
import random


logger = logging.getLogger(app_constants.log_utils)


def get_s3_client() -> boto3.client:
    """Create and return a boto3 S3 client using configured credentials.

    Falls back to environment/instance credentials if keys are not set.
    """
    try:
        kwargs = {"region_name": app_constants.s3_region}
        if app_constants.aws_access_key_id and app_constants.aws_secret_access_key:
            kwargs.update({
                "aws_access_key_id": app_constants.aws_access_key_id,
                "aws_secret_access_key": app_constants.aws_secret_access_key,
            })
        return boto3.client("s3", **kwargs)
    except Exception as e:
        logger.error(f"failed to create s3 client: {e}")
        raise e from None


def upload_to_s3(s3_client: boto3.client, file_path: str, s3_key: str, retries: int = 5, bucket_name: str = None):
    """Uploads a file to the S3 bucket with retries."""
    bucket = bucket_name or app_constants.s3_bucket_name
    attempt = 0
    last_error = None
    while attempt <= retries:
        try:
            # Try with ACL first, fallback to no ACL if bucket doesn't support it
            try:
                s3_client.upload_file(
                    file_path,
                    bucket,
                    s3_key,
                    ExtraArgs={"ACL": "public-read"},
                )
            except Exception as acl_error:
                # If ACL fails, try without ACL
                if "does not allow ACLs" in str(acl_error) or "AccessControlListNotSupported" in str(acl_error):
                    logger.warning(f"ACL not supported for bucket {bucket}, uploading without ACL")
                    s3_client.upload_file(file_path, bucket, s3_key)
                else:
                    raise acl_error
            return
        except Exception as e:
            last_error = e
            if attempt == retries:
                break
            delay = min(10, (2**attempt) + random.uniform(0, 0.5))
            time.sleep(delay)
            attempt += 1
    raise RecoverError(
        "Failed to upload to S3", {"path": file_path, "bucket": bucket, "error": str(last_error)}
    ) from None


def is_idle(s3_client: boto3.client) -> bool:
    """Fetches status.json from S3 and checks if the backend is idle."""
    try:
        response = s3_client.get_object(
            Bucket=app_constants.s3_bucket_name, Key=app_constants.status_json
        )
        status_data = response["Body"].read().decode("utf-8")
        status_json: Dict[str, str] = json.loads(status_data)
        return status_json.get("status") == "idle"
    except Exception as e:
        logger.error(f"Error fetching or reading status.json: {e}")
        return False
