import os
import logging
import boto3
import json
from lib.constants import *

def create_folder(folder_path: str):
    """Create a folder if it does not exist."""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Created folder: {folder_path}")
        else:
            logging.info(f"Folder already exists: {folder_path}")
    except Exception as e:
        logging.error(f"Failed to create folder {folder_path}: {e}")

def export_string(content: str, file_name: str, encoding="utf-8"):
    """Export a string to a file."""
    try:
        with open(file_name, "w", encoding=encoding) as file:
            file.write(content)
        logging.info(f"Exported content to file: {file_name}")
    except Exception as e:
        logging.error(f"Failed to export content to file {file_name}: {e}")

def upload_to_s3(s3_client, file_path, s3_key):
    """Uploads a file to the S3 bucket and makes it public."""
    try:
        s3_client.upload_file(
            file_path,
            s3_bucket_name,
            s3_key,
            ExtraArgs={"ACL": "public-read"}  # Make the file public
        )
        logging.info(f"Successfully uploaded {file_path} to S3 bucket {s3_bucket_name} with public access.")
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
    except Exception as e:
        logging.error(f"Failed to upload {file_path} to S3: {e}")

def is_idle(s3_client):
    """Fetches the status.json from S3 and checks if the backend is idle."""
    try:
        # Fetch the status.json file from the S3 bucket
        response = s3_client.get_object(Bucket=s3_bucket_name, Key=status_out_name)
        
        # Read the contents of the file
        status_data = response['Body'].read().decode('utf-8')
        status_json = json.loads(status_data)
        
        # Check if the status is idle
        if status_json.get("status") == "idle":
            logging.info("Backend status: idle")
            return True
        else:
            logging.info("Backend status: busy")
            return False
    except Exception as e:
        logging.error(f"Error fetching or reading status.json: {e}", exc_info=True)
        return False
