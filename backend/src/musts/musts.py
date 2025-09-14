import logging
from bs4 import BeautifulSoup

from config import app_constants
from musts.io import load_departments, write_musts
from musts.fetch import get_department_page
from musts.parse import extract_dept_node
from utils.s3 import upload_to_s3, is_idle, get_s3_client
from utils.run import busy_idle
from errors import RecoverError
from utils.http import get_http_session


logger = logging.getLogger(app_constants.log_musts)


def run_musts():
    """Fetch and export 'must' courses, updating status on S3."""
    try:
        data_dir = app_constants.data_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        # Initialize S3 client
        s3_client = get_s3_client()

        # Do not start if system is busy
        if not is_idle(s3_client):
            return "busy"

        logger.info("Starting the process to fetch must courses.")

        with busy_idle(s3_client):
            session = get_http_session()

            departments = load_departments()
            if not departments:
                raise RecoverError(app_constants.noDeptsErrMsg) from None

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
        raise RecoverError("Musts proccess failed", {"error": str(e)}) from None
    except Exception as e:
        raise e from None
