import logging
from typing import Iterable, Tuple

from backend.src.errors import S3Error
from src.utils.s3 import upload_to_s3


def publish_files(
    files: Iterable[Tuple[str, str]],
    last_updated: Tuple[str, str],
    *,
    logger: logging.Logger,
) -> None:
    """Upload data files first, then lastUpdated.json as the publish signal.

    files: iterable of (local_path, s3_key) tuples
    last_updated: (local_path, s3_key) for the lastUpdated file
    """
    try:    
        # Upload all files except lastUpdated
        for path, key in files:
            upload_to_s3(path, key)
            logger.info(f"uploaded {key}")
        # Upload the publish signal last
        lu_path, lu_key = last_updated
        upload_to_s3(lu_path, lu_key)
        logger.info(f"uploaded {lu_key} (publish signal)")
    except Exception as e:
        raise S3Error(f"Failed to publish files, error: {str(e)}") from e