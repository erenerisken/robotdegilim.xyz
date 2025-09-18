import logging
from bs4 import BeautifulSoup

from src.config import app_constants
from src.musts.io import load_departments, write_musts
from src.musts.fetch import get_department_page
from src.musts.parse import extract_dept_node
from src.utils.s3 import upload_to_s3, get_s3_client
from src.errors import RecoverError
from src.utils.http import get_http_session


logger = logging.getLogger(app_constants.log_musts)


def run_musts():
    """Fetch and export 'must' courses.

    Busy/idle lifecycle is managed by the API layer now; this function assumes
    the caller has already marked the system busy.
    """
    try:
        data_dir = app_constants.data_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        s3_client = get_s3_client()

        logger.info("Starting the process to fetch must courses.")
        session = get_http_session()

        departments = load_departments()
        if not departments:
            raise RecoverError(app_constants.noDeptsErrMsg)

        data = {}
        dept_len = len(departments.keys())
        for index, dept_code in enumerate(departments.keys(), start=1):
            if (
                not departments[dept_code].get("p")
                or departments[dept_code]["p"] in app_constants.no_prefix_variants
            ):
                continue
            response = get_department_page(session, dept_code)
            dept_soup = BeautifulSoup(response.text, "html.parser")
            dept_node = extract_dept_node(dept_soup)
            data[departments[dept_code]["p"]] = dept_node
            if index % 10 == 0:
                progress = (index / dept_len) * 100
                logger.info(f"completed {progress:.2f}% ({index}/{dept_len})")

            data_path = write_musts(data)
            upload_to_s3(s3_client, data_path, app_constants.musts_json)

        logger.info("Process to fetch must courses has ended.")
    except RecoverError as e:
        raise RecoverError(f"Musts process failed, error: {str(e)}") from e
    except Exception as e:
        raise e
