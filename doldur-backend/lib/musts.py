import requests
from bs4 import BeautifulSoup
from lib.constants import *
from lib.musts_helpers import *
from lib.helpers import *
import logging


def run_musts():
    """Main function to run the process of fetching and exporting must courses."""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        if not is_idle(s3_client):
            return "busy"

        status={"status":"busy"}
        data_path=write_status(status)
        upload_to_s3(s3_client, data_path, status_out_name)

        logging.info("Starting the process to fetch must courses.")

        create_folder(export_folder)
        session = requests.Session()

        departments = get_departments()
        if not departments:
            logging.error("No departments data available. Exiting process.")
            raise RecoverException()

        data = {}
        dept_len=len(departments.keys())
        for index,dept_code in enumerate(departments.keys(),start=1):
            if departments[dept_code]["p"] in ["-no course-", "-", ""]:
                continue
            
            response = get_department_page(session, dept_code)
            dept_soup = BeautifulSoup(response.text, "html.parser")
            dept_node = extract_dept_node(dept_soup)
            data[departments[dept_code]["p"]] = dept_node
            if index%10==0:
                progress=(index/dept_len)*100
                logging.info(f"completed {progress:.2f}% ({index}/{dept_len})")
            
        data_path=write_musts(data)
        upload_to_s3(s3_client, data_path, musts_out_name)

        status={"status":"idle"}
        data_path=write_status(status)
        upload_to_s3(s3_client, data_path, status_out_name)

        logging.info("Process to fetch must courses has ended.")

    except Exception as e:
        logging.error(
            f"An error occurred in the must courses fetching process: {e}",
            exc_info=True,
        )
        raise
    except RecoverException as e:
        logging.error(f"Recovering...",)
        status={"status":"idle"}
        data_path=write_status(status)
        upload_to_s3(s3_client, data_path, status_out_name)