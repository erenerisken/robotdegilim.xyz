from contextlib import contextmanager
import logging
import boto3

from services.status_service import set_busy, set_idle
from config import app_constants


logger = logging.getLogger(app_constants.log_app)


@contextmanager
def busy_idle(s3_client: boto3.client):
    """Context manager that marks system busy on enter and idle on exit.

    Ensures idle even if an exception bubbles out.
    """
    try:
        set_busy(s3_client)
        yield
    finally:
        try:
            set_idle(s3_client)
        except Exception as e:
            logger.error(f"failed to set idle: {e}")
