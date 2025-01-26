import requests
from bs4 import BeautifulSoup
import os
import json
from lib.scrape_helpers import *
from lib.helpers import *
from lib.constants import *
import logging
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import pytz

def run_scrape():
    """Main function to run the scraping process."""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        if not is_idle(s3_client):
            return "busy"

        status={"status":"busy"}
        data_path=write_status(status)
        upload_to_s3(s3_client, data_path, status_out_name)

        logging.info("Starting the scraping process.")

        create_folder(export_folder)        
        session = requests.Session()
        response = get_main_page(session)
        main_soup = BeautifulSoup(response.text, 'html.parser')

        dept_codes = []
        dept_names = {}
        dept_prefixes = load_prefixes()

        extract_departments(main_soup, dept_codes, dept_names)
        current_semester = extract_current_semester(main_soup)

        data = {}
        dept_len=len(dept_codes)
        for index,dept_code in enumerate(dept_codes,start=1):
            try:
                response = get_dept(session, dept_code, current_semester[0])
                dept_soup = BeautifulSoup(response.text, 'html.parser')
                
                if not any_course(dept_soup):
                    dept_prefixes[dept_code] = '-no course-'
                    continue
                
                course_codes = []
                course_names = {}
                extract_courses(dept_soup, course_codes, course_names)

                if not course_codes:
                    dept_prefixes[dept_code] = '-no course-'
                    continue
                
                if dept_code not in dept_prefixes or not dept_prefixes[dept_code]:
                    dept_prefix = get_department_prefix(session, dept_code, course_codes[0])
                    if dept_prefix:
                        dept_prefixes[dept_code] = dept_prefix

                for course_code in course_codes:
                    course_node = {}

                    response = get_course(session, course_code)
                    course_soup = BeautifulSoup(response.text, 'html.parser')

                    course_node["Course Code"] = course_code
                    if dept_code not in dept_prefixes or not dept_prefixes[dept_code]:
                        course_node["Course Name"] = dept_code + " - " + course_names[course_code]
                    else:
                        course_node["Course Name"] = deptify(dept_prefixes[dept_code], course_code) + " - " + course_names[course_code]
                    
                    sections = {}
                    extract_sections(session, course_soup, sections)
                    course_node["Sections"] = sections

                    data[int(course_code)] = course_node
                if index%10==0:
                    progress=(index/dept_len)*100
                    logging.info(f"completed {progress:.2f}% ({index}/{dept_len})")


            except Exception as e:
                raise RecoverException("Failed to process dept",{"dept_code":dept_code,"error":str(e)}) from None

        departments_json = {}
        for dept_code in dept_codes:
            if dept_code not in dept_prefixes or not dept_prefixes[dept_code]:
                departments_json[dept_code] = {"n": dept_names[dept_code], "p": "-"}
            else:
                departments_json[dept_code] = {"n": dept_names[dept_code], "p": dept_prefixes[dept_code]}

        # Saving to files
        departments_path = os.path.join(export_folder, departments_out_name)
        data_path = os.path.join(export_folder, data_out_name)
        
        last_updated_path = os.path.join(export_folder, last_updated_out_name)
        turkey_tz = pytz.timezone('Europe/Istanbul')
        current_time = datetime.now(turkey_tz)
        formatted_time = current_time.strftime('%d.%m.%Y, %H.%M')
        last_updated_info = {
            "t": current_semester[0] + ":" + current_semester[1],
            "u": formatted_time
        }

        write_json(departments_json,departments_path)     
        write_json(data,data_path)     
        write_json(last_updated_info,last_updated_path)
        # Upload files to S3
        upload_to_s3(s3_client,departments_path, departments_out_name)
        upload_to_s3(s3_client,data_path, data_out_name)
        upload_to_s3(s3_client,last_updated_path, last_updated_out_name)

        status={"status":"idle"}
        data_path=write_status(status)
        upload_to_s3(s3_client, data_path, status_out_name)

        logging.info("Scraping process completed successfully and files uploaded to S3.")

    except Exception as e:
        raise e from None
    except RecoverException as e:
        status={"status":"idle"}
        data_path=write_status(status)
        upload_to_s3(s3_client, data_path, status_out_name)
        raise RecoverException("Scraping proccess failed",{"error":str(e)}) from None

