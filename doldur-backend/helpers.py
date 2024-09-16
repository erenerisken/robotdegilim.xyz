import os
from bs4 import BeautifulSoup
import logging
from constants import *

def create_folder(folder_path):
    """Create a folder if it does not exist."""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Folder created: {folder_path}")
        else:
            logging.info(f"Folder already exists: {folder_path}")
    except Exception as e:
        logging.error(f"Error creating folder {folder_path}: {e}")


def export_string(content, file_name,encoding='utf-8'):
    """Export a string to a file."""
    try:
        with open(file_name, "w", encoding=encoding) as file:
            file.write(content)
            logging.info(f"String exported to file: {file_name}")
    except Exception as e:
        logging.error(f"Error exporting string to file {file_name}: {e}")