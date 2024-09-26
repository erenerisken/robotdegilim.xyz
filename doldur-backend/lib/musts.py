import requests
from bs4 import BeautifulSoup
import os
import json
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

        # Export the data to a JSON file
        data_path = os.path.join(export_folder, status_out_name)
        try:
            with open(data_path, "w", encoding="utf-8") as data_file:
                json.dump(status, data_file, ensure_ascii=False, indent=4)
            logging.info(f"Status info exported to: {data_path}")
        except IOError as e:
            logging.error(f"Failed to write data to {data_path}: {e}", exc_info=True)
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while exporting data: {e}", exc_info=True
            )

        upload_to_s3(s3_client, data_path, status_out_name)


        logging.info("Starting the process to fetch must courses.")

        # Create the export folder if it does not exist
        create_folder(export_folder)

        session = requests.Session()

        # Retrieve department data
        departments = get_departments()
        if not departments:
            logging.error("No departments data available. Exiting process.")
            return

        data = {}
        total_depts = len(departments)

        for index, dept_code in enumerate(departments.keys(), start=1):
            if departments[dept_code]["p"] in ["-no course-", "-", ""]:
                logging.warning(f"Skipping department {dept_code} due to no courses.")
                continue

            try:
                logging.info(
                    f"Processing department {index}/{total_depts}: {dept_code}"
                )

                response = get_department_page(session, dept_code)
                if not response:
                    logging.warning(
                        f"Failed to get page for department {dept_code}. Skipping."
                    )
                    continue

                dept_soup = BeautifulSoup(response.text, "html.parser")
                dept_node = extract_dept_node(dept_soup)
                data[departments[dept_code]["p"]] = dept_node
                # logging.info(f"Processed department {dept_code}.")

            except Exception as e:
                logging.error(
                    f"Error processing department {dept_code}: {e}", exc_info=True
                )

        # Export the data to a JSON file
        data_path = os.path.join(export_folder, musts_out_name)
        try:
            with open(data_path, "w", encoding="utf-8") as data_file:
                json.dump(data, data_file, ensure_ascii=False, indent=4)
            logging.info(f"Must course data exported to: {data_path}")
        except IOError as e:
            logging.error(f"Failed to write data to {data_path}: {e}", exc_info=True)
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while exporting data: {e}", exc_info=True
            )

        upload_to_s3(s3_client, data_path, musts_out_name)

        status={"status":"idle"}

        # Export the data to a JSON file
        data_path = os.path.join(export_folder, status_out_name)
        try:
            with open(data_path, "w", encoding="utf-8") as data_file:
                json.dump(status, data_file, ensure_ascii=False, indent=4)
            logging.info(f"Status info exported to: {data_path}")
        except IOError as e:
            logging.error(f"Failed to write data to {data_path}: {e}", exc_info=True)
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while exporting data: {e}", exc_info=True
            )

        upload_to_s3(s3_client, data_path, status_out_name)

        logging.info("Process to fetch must courses has ended.")

    except Exception as e:
        logging.error(
            f"An error occurred in the must courses fetching process: {e}",
            exc_info=True,
        )
        raise
