import os
import logging
import boto3
import json
from lib.constants import *
from lib.exceptions import RecoverException
from datetime import datetime, timedelta
import time
from logging.handlers import SMTPHandler

logger=logging.getLogger(shared_logger)

last_request_time = None

def create_folder(folder_path: str):
    """Create a folder if it does not exist."""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    except Exception as e:
        raise RecoverException(f"Failed to create folder",{"path":folder_path,"error":str(e)}) from None

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
        raise RecoverException("Failed to upload to S3",{"path":file_path,"error":str(e)}) from None

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
        logger.error(f"Error fetching or reading status.json: {e}")
        return False

def write_status(status: dict):
    data_path = os.path.join(export_folder, status_out_name)
    try:
        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(status, data_file, ensure_ascii=False, indent=4)
            return data_path
    except Exception as e:
        raise RecoverException("Failed to export status",{"error":str(e)}) from None

def check_delay(delay: int = 1):
    global last_request_time
    now = datetime.now()
    if last_request_time and now - last_request_time < timedelta(seconds=delay):
        time.sleep(delay - (now - last_request_time).total_seconds())
        now=datetime.now()
    last_request_time = now

# Configure email handler
def get_email_handler():
    try:
        mail_handler = SMTPHandler(
            mailhost=(MAIL_SERVER, MAIL_PORT),
            fromaddr=MAIL_DEFAULT_SENDER,
            toaddrs=[MAIL_RECIPIENT],
            subject="Error in Robotdegilim",
            credentials=(MAIL_USERNAME, MAIL_PASSWORD),
            secure=()  # Use TLS
        )
        
        mail_handler.setLevel(logging.ERROR)  # Only send email for errors
        mail_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        return mail_handler
    except Exception as e:
        logger.error("Failed to create email handler: "+str(e))
        return None