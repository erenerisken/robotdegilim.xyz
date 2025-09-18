import logging
from datetime import datetime

from bs4 import BeautifulSoup

from src.scrape.fetch import (
    get_main_page,
    get_dept,
    get_department_prefix,
    get_course,
)
from src.scrape.parse import (
    any_course,
    extract_courses,
    extract_sections,
    extract_departments,
    extract_current_semester,
    deptify,
)
from src.scrape.io import load_prefixes_combined
from src.utils.io import write_json
from src.utils.s3 import is_idle, get_s3_client
from src.utils.publish import publish_files
from src.utils.run import busy_idle
from src.config import app_constants
from src.errors import RecoverError
from src.utils.http import get_http_session

logger = logging.getLogger(app_constants.log_scrape)


def run_scrape():
    """Main function to run the scraping process."""
    try:
        # Initialize S3 client
        s3_client = get_s3_client()

        if not is_idle(s3_client):
            return "busy"

        logger.info("Starting the scraping process.")

        data_dir = app_constants.data_dir
        data_dir.mkdir(parents=True, exist_ok=True)

        with busy_idle(s3_client):
            session = get_http_session()
            response = get_main_page(session)
            main_soup = BeautifulSoup(response.text, "html.parser")

            dept_codes = []
            dept_names = {}
            dept_prefixes = load_prefixes_combined()

            extract_departments(main_soup, dept_codes, dept_names)
            current_semester = extract_current_semester(main_soup)

            data = {}
            dept_len = len(dept_codes)
            for index, dept_code in enumerate(dept_codes, start=1):
                try:
                    response = get_dept(session, dept_code, current_semester[0])
                    dept_soup = BeautifulSoup(response.text, "html.parser")

                    if not any_course(dept_soup):
                        if dept_code not in dept_prefixes:
                            dept_prefixes[dept_code] = "-no course-"
                        continue

                    course_codes = []
                    course_names = {}
                    extract_courses(dept_soup, course_codes, course_names)

                    if not course_codes:
                        if dept_code not in dept_prefixes:
                            dept_prefixes[dept_code] = "-no course-"
                        continue

                    if (
                        dept_code not in dept_prefixes
                        or dept_prefixes[dept_code] in app_constants.no_prefix_variants
                    ):
                        dept_prefix = get_department_prefix(session, dept_code, course_codes[0])
                        if dept_prefix:
                            dept_prefixes[dept_code] = dept_prefix
                        else:
                            dept_prefixes[dept_code] = "-"

                    for course_code in course_codes:
                        course_node = {}

                        response = get_course(session, course_code)
                        course_soup = BeautifulSoup(response.text, "html.parser")

                        course_node["Course Code"] = course_code
                        if (
                            dept_code not in dept_prefixes
                            or dept_prefixes[dept_code] in app_constants.no_prefix_variants
                        ):
                            course_node["Course Name"] = (
                                course_code + " - " + course_names[course_code]
                            )
                        else:
                            course_node["Course Name"] = (
                                deptify(dept_prefixes[dept_code], course_code)
                                + " - "
                                + course_names[course_code]
                            )

                        sections = {}
                        extract_sections(session, course_soup, sections)
                        course_node["Sections"] = sections

                        data[int(course_code)] = course_node
                    if index % 10 == 0:
                        progress = (index / dept_len) * 100
                        logger.info(f"completed {progress:.2f}% ({index}/{dept_len})")

                except Exception as e:
                    raise RecoverError(
                        f"Failed to process dept: dept_code: {dept_code}"
                    ) from e

            departments_json = {}
            departments_noprefix = {}
            for dept_code in dept_codes:
                departments_json[dept_code] = {
                    "n": dept_names[dept_code],
                    "p": dept_prefixes[dept_code],
                }
                if dept_prefixes[dept_code] in app_constants.no_prefix_variants:
                    departments_noprefix[dept_code] = {
                        "n": dept_names[dept_code],
                        "p": dept_prefixes[dept_code],
                    }

            # Saving to files
            departments_path = app_constants.data_dir / app_constants.departments_json
            manual_prefixes_path = app_constants.data_dir / app_constants.manual_prefixes_json
            departments_noprefix_path = (
                app_constants.data_dir / app_constants.departments_noprefix_json
            )
            data_path = app_constants.data_dir / app_constants.data_json

            last_updated_path = app_constants.data_dir / app_constants.last_updated_json
            turkey_tz = app_constants.TR_TZ
            current_time = datetime.now(turkey_tz)
            formatted_time = current_time.strftime("%d.%m.%Y, %H.%M")
            last_updated_info = {
                "t": current_semester[0] + ":" + current_semester[1],
                "u": formatted_time,
            }

            write_json(departments_noprefix, departments_noprefix_path)
            write_json(departments_json, departments_path)
            write_json(data, data_path)
            write_json(last_updated_info, last_updated_path)

            # Upload files to S3: data files first, lastUpdated last
            upload_list = [
                (departments_noprefix_path, app_constants.departments_noprefix_json),
                (departments_path, app_constants.departments_json),
                (data_path, app_constants.data_json),
            ]
            if manual_prefixes_path.exists():
                upload_list.append((manual_prefixes_path, app_constants.manual_prefixes_json))
            else:
                logger.warning(
                    "manualPrefixes.json missing at %s; skipping upload",
                    str(manual_prefixes_path),
                )

            publish_files(
                s3_client,
                files=upload_list,
                last_updated=(last_updated_path, app_constants.last_updated_json),
                logger=logger,
            )

        logger.info("Scraping process completed successfully and files uploaded to S3.")

    except RecoverError as e:
        raise RecoverError("Scraping proccess failed") from e
    except Exception as e:
        raise e
