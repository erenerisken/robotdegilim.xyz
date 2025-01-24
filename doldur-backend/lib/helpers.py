import os
import logging
import boto3
import json
from lib.constants import *
from lib.exceptions import RecoverException

def create_folder(folder_path: str):
    """Create a folder if it does not exist."""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    except Exception as e:
        logging.error(f"Failed to create folder {folder_path}: {e}")
        raise RecoverException()

def upload_to_s3(s3_client, file_path, s3_key):
    """Uploads a file to the S3 bucket and makes it public."""
    try:
        s3_client.upload_file(
            file_path,
            s3_bucket_name,
            s3_key,
            ExtraArgs={"ACL": "public-read"}  # Make the file public
        )
    except Exception as e:
        logging.error(f"Failed to upload {file_path} to S3: {e}")
        raise RecoverException()

def is_idle(s3_client):
    """Fetches the status.json from S3 and checks if the backend is idle."""
    try:
        response = s3_client.get_object(Bucket=s3_bucket_name, Key=status_out_name)
        status_data = response['Body'].read().decode('utf-8')
        status_json = json.loads(status_data)
        if status_json.get("status") == "idle":
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error fetching or reading status.json: {e}", exc_info=True)
        return False

def write_status(status: dict):
    data_path = os.path.join(export_folder, status_out_name)

    try:
        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(status, data_file, ensure_ascii=False, indent=4)
            return data_path
    except Exception as e:
        logging.error(f"An unexpected error occurred while exporting data: {e}", exc_info=True)
        raise RecoverException()