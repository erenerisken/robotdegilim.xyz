from bs4 import BeautifulSoup
import logging
import requests
import sys
from constants import *
import os
import json
from urllib.parse import urlparse, parse_qs

def get_departments():
    """Find the most recent departments JSON file from export_folder and return its contents as a dictionary."""
    try:
        # Get a list of all JSON files in the export_folder
        json_files = [f for f in os.listdir(export_folder) if f.endswith(departments_out_name)]
        
        if not json_files:
            raise FileNotFoundError("No departments JSON files found in the export folder.")
        if len(json_files)!=1:
            raise Exception("Multiple departments.json file in export folder.")
        # Determine the most recent semester
        file_path = os.path.join(export_folder, departments_out_name)
        
        # Read and return the JSON content
        with open(file_path, 'r', encoding='utf-8') as file:
            departments = json.load(file)
        logging.info(f"Successfully read the file: {file_path}")
        return departments

    except Exception as e:
        logging.error(f"An error occurred while reading the departments: {e}")
        logging.info("Program terminated...")
        sys.exit()

def get_department_page(session,dept_code):
    """Fetch department catalog page using session"""
    try:
        response = session.get(department_catalog_url.replace('{dept_code}',str(dept_code)), headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response.encoding = "utf-8"
        #logging.info("Successfully fetched the department catalog page.")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred when fetching the department catalog page: {e}")
        return False

def extract_course_code(course_link):
    """Extract the course code from a course URL."""
    try:
        # Parse the URL
        parsed_url = urlparse(course_link)
        
        # Extract the query parameters
        query_params = parse_qs(parsed_url.query)
        
        # Retrieve the 'course_code' parameter
        course_code = query_params.get('course_code', [None])[0]
        
        if course_code:
            #logging.info(f"Extracted course code: {course_code}")
            return course_code
        else:
            logging.error(f"No course code found in URL: {course_link}")
            return None
    except Exception as e:
        logging.error(f"An error occurred while extracting the course code from {course_link}: {e}")
        return None