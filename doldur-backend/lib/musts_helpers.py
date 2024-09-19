import requests
from lib.constants import *
import os
import json
from urllib.parse import urlparse, parse_qs
import logging

def get_departments():
    """Find the departments JSON file from export_folder and return its contents as a dictionary."""
    file_path = os.path.join(export_folder, departments_out_name)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            departments = json.load(file)
            logging.info(f"Loaded departments from {file_path}")
            return departments
    except FileNotFoundError:
        logging.error(f"Departments file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {file_path}")
        return {}
    except Exception as e:
        logging.error(f"Failed to load departments from file {file_path}: {e}")
        return {}

def get_department_page(session: requests.Session, dept_code: str):
    """Fetch department catalog page using session."""
    try:
        response = session.get(
            department_catalog_url.replace("{dept_code}", str(dept_code)), headers=headers
        )
        response.encoding = "utf-8"
        if response.status_code == 200:
            #logging.info(f"Successfully fetched department page for {dept_code}")
            pass
        else:
            logging.warning(f"Failed to fetch department page for {dept_code}. Status code: {response.status_code}")
        return response
    except requests.RequestException as e:
        logging.error(f"Request failed for department {dept_code}: {e}")
        return None

def extract_course_code(course_link: str):
    """Extract the course code from a course URL."""
    try:
        parsed_url = urlparse(course_link)
        query_params = parse_qs(parsed_url.query)
        course_code = query_params.get("course_code", [None])[0]
        if course_code:
            #logging.debug(f"Extracted course code: {course_code}")
            pass
        else:
            logging.warning(f"Course code not found in link: {course_link}")
        return course_code
    except Exception as e:
        logging.error(f"Failed to extract course code from link {course_link}: {e}")
        return None

def extract_dept_node(dept_soup):
    """Extract department node data from BeautifulSoup object."""
    dept_node = {}
    try:
        semester_tables = dept_soup.find('div', {"class": "field-body"}).find_all('table')
        semester_tables = semester_tables[:-1]  # Skip the last table

        for sem_no, semester_table in enumerate(semester_tables,start=1):
            courses = []
            rows = semester_table.find_all('tr')
            if not rows:
                continue
            rows = rows[1:]  # Skip the header row

            for row in rows:
                cells = row.find_all('td')
                if not cells:
                    continue
                if len(cells) != 6:
                    break

                course_link = cells[0].find('a')
                if course_link:
                    course_link = course_link.get('href')
                    course_code = extract_course_code(course_link)
                    if course_code:
                        courses.append(course_code)

            if courses:
                dept_node[sem_no] = courses
        #logging.info(f"Extracted department node data successfully")
    except Exception as e:
        logging.error(f"Failed to extract department node data: {e}")
    return dept_node
