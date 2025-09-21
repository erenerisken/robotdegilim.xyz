from contextlib import contextmanager
import logging
import boto3

from src.services.status_service import set_busy, set_idle
from src.config import app_constants


logger = logging.getLogger(app_constants.log_app)


@contextmanager
def busy_idle():
    """Context manager that marks system busy on enter and idle on exit.

    Ensures idle even if an exception bubbles out.
    """
    try:
        set_busy()
        yield
    finally:
        try:
            set_idle()
        except Exception as e:
            logger.error(f"failed to set idle, error: {str(e)}")
