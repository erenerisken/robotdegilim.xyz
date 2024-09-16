import requests
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
        logging.FileHandler("scrape.log",encoding='utf-8'),
        logging.StreamHandler()
    ]
)

from scrape_helpers import *
from helpers import *

# If does not exist creates export folder
create_folder(export_folder)

# Start a session for making requests
session = requests.Session()

# Fetch the main page
response=get_main_page(session)

# export main page
#export_string(response.text,"main.html")

# Parse the HTML content of main page with BeautifulSoup
main_soup = BeautifulSoup(response.text, 'html.parser')

# List and dictionaries for department codes and names and prefixes
dept_codes = []
dept_names = {}
dept_prefixes={}

# Extract all options from the <select> tag with name="select_dept"
extract_departments(main_soup,dept_codes,dept_names)

# Extract the current semester from the <select> tag with name="select_semester"
current_semester=extract_current_semester(main_soup)

# data to export
data={}

logging.info("Process of fetching all data has started")
total_departments=len(dept_codes)
# Iterate over dept_codes
for i,dept_code in enumerate(dept_codes):
    logging.info(f"Department {i+1}/{total_departments}")
    logging.info(f"Department code: {dept_code}")

    # Fetches department page
    response=get_dept(session,dept_code,current_semester[0])
    # If error occurs when fetching department page then continue
    if not response:
        continue

    # Export department page
    #export_string(response.text,"department.html")

    # Parse the HTML content of department page
    dept_soup=BeautifulSoup(response.text,'html.parser')

    # Check for error message it is appears when a department has no course
    if not any_course(dept_soup,dept_code):
        dept_prefixes[dept_code]='-no course-'
        logging.warning(f"Any course not found with this department: {dept_code}")
        continue
    
    # To Store course codes and names
    course_codes=[]
    course_names={}
    # Extract course codes and names from department page
    extract_courses(dept_soup,course_codes,course_names)

    # To eliminate errors
    if not course_codes:
        dept_prefixes[dept_code]='-no course-'
        logging.warning(f"Any course not found with this department: {dept_code}")
        continue
    
    # Fetching department prefix from catalog page of first course in the list
    if dept_code not in dept_prefixes or not dept_prefixes[dept_code]:
        dept_prefix=get_department_prefix(session,dept_code,course_codes[0])
        if dept_prefix:
            dept_prefixes[dept_code]=dept_prefix

    # Iterate over course_codes
    for course_code in course_codes:        
        course_node={}

        # Fetching course page
        response=get_course(session,course_code)
        # If error occurs when fetching course page then continue
        if not response:
            continue

        # Export course page
        #export_string(response.text,"course.html")

        # Parse the HTML content of course page
        course_soup=BeautifulSoup(response.text,'html.parser')


        # Fill the node
        course_node["Course Code"]=course_code
        if dept_code not in dept_prefixes or not dept_prefixes[dept_code]:
            course_node["Course Name"]=dept_code+" - "+course_names[course_code]
        else:
            course_node["Course Name"]=deptify(dept_prefixes[dept_code],course_code)+" - "+course_names[course_code]
        
        #if "SUMMER PRACTICE" in course_node["Course Name"]:
        #    continue

        # Extract sections and their informations
        sections={}
        extract_sections(session,course_soup,sections)
        course_node["Sections"]=sections

        # Writing to data object
        data[int(course_code)]=course_node

# Exporting department list as JSON
departments_json = {}
for dept_code in dept_codes:
    if dept_code not in dept_prefixes or not dept_prefixes[dept_code]:
        departments_json[dept_code] = {'n': dept_names[dept_code], 'p': '-'}
    else:
        departments_json[dept_code] = {'n': dept_names[dept_code], 'p': dept_prefixes[dept_code]}

departments_path = os.path.join(export_folder, departments_out_name)
with open(departments_path, "w", encoding="utf-8") as departments_file:
    json.dump(departments_json, departments_file, ensure_ascii=False, indent=4)
logging.info(f"Departments exported to: {departments_path}")

# Export data object as JSON
current_datetime = datetime.now()
data_path = os.path.join(export_folder, data_out_name)
with open(data_path, "w", encoding="utf-8") as data_file:
    json.dump(data, data_file, ensure_ascii=False, indent=4)
logging.info(f"Course data exported to: {data_path}")
