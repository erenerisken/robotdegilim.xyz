import logging
from typing import Iterable, Tuple
import boto3

from src.utils.s3 import upload_to_s3


def publish_files(
    s3_client: boto3.client,
    files: Iterable[Tuple[str, str]],
    last_updated: Tuple[str, str],
    *,
    logger: logging.Logger,
) -> None:
    """Upload data files first, then lastUpdated.json as the publish signal.

    files: iterable of (local_path, s3_key) tuples
    last_updated: (local_path, s3_key) for the lastUpdated file
    """
    # Upload all files except lastUpdated
    for path, key in files:
        upload_to_s3(s3_client, path, key)
        logger.info(f"uploaded {key}")
    # Upload the publish signal last
    lu_path, lu_key = last_updated
    upload_to_s3(s3_client, lu_path, lu_key)
    logger.info(f"uploaded {lu_key} (publish signal)")
