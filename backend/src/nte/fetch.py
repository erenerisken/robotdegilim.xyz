import logging
import json
from typing import Dict, Any

from src.config import app_constants
from src.utils.http import get_http_session, get
from src.errors import RecoverError

logger = logging.getLogger(app_constants.log_nte)


def fetch_courses_data() -> Dict[str, Any]:
    """Fetch courses data from S3."""
    try:
        session = get_http_session()
        response = get(
            session, 
            app_constants.courses_s3_url,
            name="fetch_courses_data",
            base_delay=1.0
        )
        response.encoding = "utf-8"
        return json.loads(response.text)
    except Exception as e:
        raise RecoverError(
            "Failed to fetch courses data from S3",
            {"url": app_constants.courses_s3_url, "error": str(e)}
        ) from e


def fetch_departments_data() -> Dict[str, Any]:
    """Fetch departments data from S3."""
    try:
        session = get_http_session()
        response = get(
            session,
            app_constants.departments_s3_url,
            name="fetch_departments_data",
            base_delay=1.0
        )
        response.encoding = "utf-8"
        return json.loads(response.text)
    except Exception as e:
        raise RecoverError(
            "Failed to fetch departments data from S3",
            {"url": app_constants.departments_s3_url, "error": str(e)}
        ) from e


def fetch_nte_data() -> Dict[str, Any]:
    """Fetch NTE list data from S3."""
    try:
        session = get_http_session()
        response = get(
            session,
            app_constants.nte_list_s3_url,
            name="fetch_nte_data",
            base_delay=1.0
        )
        response.encoding = "utf-8"
        return json.loads(response.text)
    except Exception as e:
        raise RecoverError(
            "Failed to fetch NTE list from S3",
            {"url": app_constants.nte_list_s3_url, "error": str(e)}
        ) from e 