import logging
import requests

from src.config import app_constants
from src.errors import RecoverError
from src.utils.timing import throttle_before_request, report_success, report_failure


logger = logging.getLogger(app_constants.log_musts)


def get_department_page(session: requests.Session, dept_code: str, tries: int = 5):
    attempt = 0
    while attempt < tries:
        try:
            throttle_before_request(1.0)
            response = session.get(
                app_constants.department_catalog_url.replace("{dept_code}", str(dept_code)),
            )
            response.encoding = "utf-8"
            if response.status_code == 200:
                report_success()
                return response
        except Exception as e:
            report_failure()
            raise RecoverError(
                "Request failed", {"dept_code": dept_code, "error": str(e)}
            ) from None

        attempt += 1
    raise RecoverError(
        "Failed to get department page", {"dept_code": dept_code, "trials": tries}
    ) from None
