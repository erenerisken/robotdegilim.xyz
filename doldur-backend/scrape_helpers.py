from bs4 import BeautifulSoup
import logging
import requests
import sys
from constants import *

def get_main_page(session):
    """Fetch oibs64 main page using session"""
    try:
        response = session.get(oibs64_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response.encoding = "utf-8"
        #logging.info("Successfully fetched the oibs64 main page.")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred when fetching the oibs64 main page: {e}")
        logging.info("Program terminated...")
        sys.exit()

def get_dept(session, dept_code, semester_code):
    """Fetch department page using session."""
    data = {
        "textWithoutThesis": 1,
        "select_dept": dept_code,
        "select_semester": semester_code,
        "submit_CourseList": "Submit",
        "hidden_redir": "Login",
    }
    try:
        response = session.post(oibs64_url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response.encoding = "utf-8"
        #logging.info(f"Successfully fetched the {semester_code}:{dept_code} page.")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(
            f"An error occurred when fetching the {semester_code}:{dept_code} page: {e}"
        )
        return False

def get_course(session, course_code):
    """Fetch course page using session."""
    data = {
        "SubmitCourseInfo": "Course Info",
        "text_course_code": course_code,
        "hidden_redir": "Course_List",
    }
    try:
        response = session.post(oibs64_url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response.encoding = "utf-8"
        #logging.info(f"Successfully fetched the course page. course_code:{course_code}")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(
            f"An error occurred when fetching the course page. course_code:{course_code}, error: {e}"
        )
        return False

def get_section(session, section_code):
    """Fetch section page using session."""
    data = {"submit_section": section_code, "hidden_redir": "Course_Info"}
    try:
        response = session.post(oibs64_url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response.encoding = "utf-8"
        #logging.info(f"Successfully fetched the section page. section_code:{section_code}")
        return response
    except requests.exceptions.RequestException as e:
        logging.error(
            f"An error occurred when fetching the course page. section_code:{section_code}, error: {e}"
        )
        return False

def get_department_prefix(session, dept_code, course_code):
    """Fetch department prefix from course catalog page with using session"""
    try:
        response = session.get(
            course_catalog_url.replace("{dept_code}", dept_code).replace(
                "{course_code}", course_code
            ),
            headers=headers,
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        response.encoding = "utf-8"
        #logging.info(f"Successfully fetched the catalog page. course_code:{course_code}")
        #export_string(response.text, "catalog.html")
        catalog_soup = BeautifulSoup(response.text, "html.parser")
        h2 = catalog_soup.find("h2")
        if h2:
            course_code_with_prefix = h2.get_text().split(" ")[0]
            dept_prefix = "".join(
                [char for char in course_code_with_prefix if char.isalpha()]
            )
            if dept_prefix:
                #logging.info(f"Successfully fetched the department prefix. {dept_code}:{dept_prefix}")
                return dept_prefix
        logging.error(f"Could not fetched the prefix of {dept_code}")
        return False
    except Exception as e:
        logging.error(f"An error occurred when fetching the prefix of {dept_code}: {e}")
        return False

def extract_departments(soup, dept_codes, dept_names):
    """Extract department codes and names from the main page(soup object)."""
    dept_select = soup.find("select", {"name": "select_dept"})
    if dept_select:
        dept_options = dept_select.find_all("option")
        if dept_options:
            #logging.info("Process of fetching department names and codes has started")
            for option in dept_options:
                value = option.get("value")
                text = option.get_text()
                if value and text:
                    dept_codes.append(value)
                    dept_names[value] = text
                    #logging.info(f"'{value}:{text}' fetched")
            #logging.info("Process of fetching department names and codes has ended")
            logging.info(f"Total {len(dept_codes)} departments found")
        else:
            logging.error("No department options found in the select element")
            logging.info("Program terminated...")
            sys.exit()
    else:
        logging.error("No select element with name='select_dept' found")
        logging.info("Program terminated...")
        sys.exit()

def extract_current_semester(soup):
    """Extract the current semester from the main page(soup object)."""
    semester_select = soup.find("select", {"name": "select_semester"})
    if semester_select:
        current_semester_option = semester_select.find("option")
        if current_semester_option:
            current_semester = tuple(
                (
                    current_semester_option.get("value"),
                    current_semester_option.get_text(),
                )
            )
            logging.info(
                f"Current semester is fetched: '{current_semester[0]}:{current_semester[1]}'"
            )
            return current_semester
        else:
            logging.error("No options found in the select element for the semester")
            logging.info("Program terminated...")
            sys.exit()
    else:
        logging.error("No select element with name='select_semester' found")
        logging.info("Program terminated...")
        sys.exit()

def extract_courses(soup, course_codes, course_names):
    """Extract course codes and names from the department page(soup object)."""
    try:
        course_table = soup.find("form").find_all("table")[3]
        course_rows = course_table.find_all("tr")[1:]
        for course_row in course_rows:
            course_cells = course_row.find_all("td")

            course_code = course_cells[0].find("input").get("value")
            course_name = course_cells[2].get_text()

            course_codes.append(course_code)
            course_names[course_code] = course_name

            #logging.info(f"'{course_code}:{course_name}' fetched")
        logging.info(f"Total {len(course_codes)} courses found")
    except Exception as e:
        logging.error(
            f"An error occurred when fetching course names and codes:{course_code}:{course_name}, {e}"
        )

def extract_sections(session, soup, sections):
    """Extract sections and their informations from the course page(soup object)."""
    try:
        # The table in the HTML contains nested <tr> tags, meaning there are <tr> elements inside other <tr> elements.
        # This can cause issues when trying to parse with BeautifulSoup
        section_table = soup.find("form").find_all("table")[2]
        section_table_string = str(section_table).replace("\n", "")
        section_rows = extract_tags_as_string(section_table_string, "<tr>", "</tr>")[2:]

        for section_row in section_rows:
            section_node = {}

            time_row = extract_tags_as_string(section_row[4:-5], "<tr>", "</tr>")[0]
            section_info = section_row.replace(time_row, "")
            time_table = extract_tags_as_string(time_row, "<table>", "</table>")[0]

            section_info_soup = BeautifulSoup(section_info, "html.parser")
            time_table_soup = BeautifulSoup(time_table, "html.parser")

            info_cells = section_info_soup.find_all("td")
            time_rows = time_table_soup.find_all("tr")

            section_times = []
            for time_row in time_rows:
                time_cells = time_row.find_all("td")
                if not time_cells[0].get_text() or time_cells[0].get_text() not in days or not days[time_cells[0].get_text()]:
                    continue
                section_times.append(
                    {
                        "p": time_cells[3].find("font").get_text(),
                        "s": time_cells[1].find("font").get_text(),
                        "e": time_cells[2].find("font").get_text(),
                        "d": days[time_cells[0].get_text()],
                    }
                )

            section_code = info_cells[0].find("input").get("value")
            section_instructors = [info_cells[1].get_text(), info_cells[2].get_text()]

            # Fetch section page and extract constraints
            response = get_section(session, section_code)
            #export_string(response.text, "section.html")
            section_soup = BeautifulSoup(response.text, "html.parser")
            section_constraints = []
            form_msg = section_soup.find("div", id="formmessage").find('b').get_text()
            if not form_msg:
                extract_constraints(section_soup, section_constraints)

            section_node["i"] = section_instructors
            section_node["c"] = section_constraints
            section_node["t"] = section_times
            sections[section_code] = section_node
    except Exception as e:
        logging.error(f"An error occurred when fetching course names and codes: {e}")

def extract_constraints(soup, constraints):
    """Extracts section constraints from section page(soup object)."""
    cons_table = soup.find("form").find_all("table")[2]
    cons_rows = cons_table.find_all("tr")[1:]
    for cons_row in cons_rows:
        cons_cells = cons_row.find_all("td")
        constraints.append(
            {
                "d": cons_cells[0].get_text(),
                "s": cons_cells[1].get_text(),
                "e": cons_cells[2].get_text(),
            }
        )

def any_course(soup, dept_code):
    """Return True if formmessage contains error message else False"""
    form_msg = soup.find("div", id="formmessage").find('b').get_text()
    if form_msg:
        return False
    return True

def deptify(prefix, course_code):
    """Return course code with prefix"""
    result = "" + prefix
    if course_code[3] == "0":
        result += course_code[4:]
    else:
        result += course_code[3:]
    return result

def extract_tags_as_string(html_code, start_tag, end_tag):
    """Extracts all tags(as string) of a html code(given as string) and returns"""
    stack = []
    tags = []
    sindex = 0
    cindex = 0
    word_length = len(end_tag)
    diff = len(end_tag) - len(start_tag)

    while cindex < len(html_code):
        if (cindex + word_length) > len(html_code):  # Ensure we don't go out of bounds
            break

        # Slice the string to get the current 4-character word
        word = html_code[cindex : cindex + word_length]

        # If we find the opening tag, push it onto the stack
        if word[:-diff] == start_tag:
            if not stack:  # This means it's the start of a new top-level row
                sindex = cindex
            stack.append(start_tag)

        # If we find the closing tag, pop from the stack
        if word == end_tag:
            if len(stack) == 1:
                eindex = cindex + word_length
                tags.append(html_code[sindex:eindex])
                stack = []
            elif stack:
                stack.pop()

        cindex += 1

    return tags
