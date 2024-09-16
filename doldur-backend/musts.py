import requests
import sys
from bs4 import BeautifulSoup
import logging
import os
import json
from constants import *
from datetime import datetime

# Configure logging to output to both file and terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("musts.log",encoding='utf-8'),
        logging.StreamHandler()
    ]
)

from musts_helpers import *
from helpers import *

# If does not exist creates export folder
create_folder(export_folder)

# Start a session for making requests
session = requests.Session()

# Get departments JSON file as dictionary
departments=get_departments()
total_departments = len(departments)

data={}
logging.info("Process of fetching must courses has started")
# Iterate over department codes
for i, dept_code in enumerate(departments.keys(), start=1):
    # Skip departments without prefixes
    if departments[dept_code]['p'] in ['-no course-','-','']:
        logging.warning(f"Skipping department {dept_code} due to no courses.")
        continue
    
    logging.info(f"Processing department {i}/{total_departments} ({departments[dept_code]['n']})")
    
    # Fetch the department page
    response=get_department_page(session,dept_code)
    if not response:
        continue
    
    # Export response HTML for debugging
    #export_string(response.text,'main.html')
    
    # Parse the department page
    dept_soup=BeautifulSoup(response.text,'html.parser')
    
    dept_node={}
    try:
        semester_tables = dept_soup.find('div', {'class': 'field-body'}).find_all('table')
    except Exception as e:
        logging.error(f"Failed to find course tables for department {dept_code}: {e}")
        data[departments[dept_code]['p']]=dept_node
        continue

    # Skip the last table
    semester_tables=semester_tables[:-1]

    for sem_no,semester_table in enumerate(semester_tables):
        courses=[]
        rows=semester_table.find_all('tr')
        if not rows:
            continue
        rows=rows[1:]

        for row in rows:
            cells=row.find_all('td')
            if not cells:
                continue
            if len(cells)!=6:
                break

            course_link=cells[0].find('a')
            if course_link:
                course_link=course_link.get('href')
                course_code=extract_course_code(course_link)
                courses.append(course_code)

        dept_node[sem_no]=courses

    data[departments[dept_code]['p']]=dept_node

logging.info("Process of fetching must courses has ended")
# Export data to a JSON file
current_datetime = datetime.now()
data_path = os.path.join(export_folder, musts_out_name)
with open(data_path, "w", encoding="utf-8") as data_file:
    json.dump(data, data_file, ensure_ascii=False, indent=4)
logging.info(f"Must Course data exported to: {data_path}")
