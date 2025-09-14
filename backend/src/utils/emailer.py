import logging
from logging.handlers import SMTPHandler

from config import app_constants


def get_email_handler():
    """Create an ERROR-level SMTPHandler if mail creds are configured.

    Returns None if required values are missing or handler setup fails.
    """
    # Only configure email if credentials are present
    if not app_constants.MAIL_USERNAME or not app_constants.MAIL_PASSWORD:
        return None
    try:
        handler = SMTPHandler(
            mailhost=(app_constants.MAIL_SERVER, app_constants.MAIL_PORT),
            fromaddr=app_constants.MAIL_DEFAULT_SENDER,
            toaddrs=[app_constants.MAIL_RECIPIENT],
            subject=app_constants.MAIL_ERROR_SUBJECT,
            credentials=(app_constants.MAIL_USERNAME, app_constants.MAIL_PASSWORD),
            secure=(),  # Use TLS
        )
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        return handler
    except Exception as e:
        # Use a local logger only if available; otherwise, swallow error quietly
        try:
            logging.getLogger(app_constants.log_utils).error(f"Failed to create email handler: {e}")
        except Exception:
            pass
        return None
