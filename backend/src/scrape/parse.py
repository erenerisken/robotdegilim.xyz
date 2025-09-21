import logging
from typing import List, Dict, Tuple, cast
from bs4 import BeautifulSoup
from bs4.element import Tag
import requests

from src.config import app_constants
from src.errors import RecoverError
from src.scrape.fetch import get_section


def _strip_upper(s) -> str:
    return str(s or "").strip().upper()


logger = logging.getLogger(app_constants.log_scrape)


def extract_departments(
    soup: BeautifulSoup, dept_codes: List[str], dept_names: Dict[str, str]
) -> None:
    dept_select = soup.find("select", {"name": "select_dept"})
    if dept_select:
        dept_options = dept_select.find_all("option")
        if dept_options:
            for option in dept_options:
                value = option.get("value")
                text = option.get_text()
                if value and text:
                    value = _strip_upper(value)
                    text = (text or "").strip()
                    dept_codes.append(value)
                    dept_names[value] = text


def extract_current_semester(soup: BeautifulSoup) -> Tuple[str, str]:
    semester_select = soup.find("select", {"name": "select_semester"})
    if semester_select:
        current_semester_option = semester_select.find("option")
        if current_semester_option:
            value = _strip_upper(current_semester_option.get("value"))
            text = (current_semester_option.get_text() or "").strip()
            return (value, text)
    raise RecoverError("Could not extract current semester")


def extract_courses(
    soup: BeautifulSoup, course_codes: List[str], course_names: Dict[str, str]
) -> None:
    form = soup.find("form")
    if not form:
        return
    tables = form.find_all("table")
    if len(tables) < 4:
        return
    course_table = cast(Tag, tables[3])
    if course_table:
        course_rows = course_table.find_all("tr")[1:]
        if course_rows:
            for course_row in course_rows:
                course_cells = course_row.find_all("td")
                if course_cells and len(course_cells) >= 3:
                    course_code = course_cells[0].find("input").get("value")
                    course_name = course_cells[2].get_text()
                    if course_code and course_name:
                        course_code = _strip_upper(course_code)
                        course_name = (course_name or "").strip()
                        course_codes.append(course_code)
                        course_names[course_code] = course_name


def extract_sections(soup: BeautifulSoup, sections: Dict[str, Dict]) -> None:
    try:
        form = soup.find("form")
        if not form:
            return
        tables = form.find_all("table")
        if len(tables) < 3:
            return
        section_table = cast(Tag, tables[2])
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
                time_row = cast(Tag, time_row)
                time_cells = time_row.find_all("td")
                if (
                    not time_cells[0].get_text()
                    or time_cells[0].get_text() not in app_constants.days_dict
                ):
                    continue
                section_times.append(
                    {
                        "p": time_cells[3].find("font").get_text(),
                        "s": time_cells[1].find("font").get_text(),
                        "e": time_cells[2].find("font").get_text(),
                        "d": app_constants.days_dict[time_cells[0].get_text()],
                    }
                )

            section_code = info_cells[0].find("input").get("value")
            section_instructors = [info_cells[1].get_text(), info_cells[2].get_text()]
            response = get_section(section_code)

            section_soup = BeautifulSoup(response.text, "html.parser")
            section_constraints: List[Dict[str, str]] = []
            form_msg = section_soup.find("div", id="formmessage").find("b").get_text()
            if not form_msg:
                extract_constraints(section_soup, section_constraints)

            section_node["i"] = section_instructors
            section_node["c"] = section_constraints
            section_node["t"] = section_times
            sections[section_code] = section_node

    except Exception as e:
        raise RecoverError(f"Failed to extract sections, error: {str(e)}") from e


def extract_constraints(soup: BeautifulSoup, constraints: List[Dict[str, str]]) -> None:
    try:
        cons_table = cast(Tag, soup.find("form").find_all("table")[2])
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
    except Exception as e:
        logger.error(f"Error extracting constraints, error: {str(e)}")


def any_course(soup: BeautifulSoup) -> bool:
    form_msg = soup.find("div", id="formmessage").find("b").get_text()
    if form_msg:
        return False
    return True


def deptify(prefix: str, course_code: str) -> str:
    result = "" + prefix
    if course_code[3] == "0":
        result += course_code[4:]
    else:
        result += course_code[3:]
    return result


def extract_tags_as_string(html_code: str, start_tag: str, end_tag: str) -> List[str]:
    stack: List[str] = []
    tags: List[str] = []
    sindex = 0
    cindex = 0
    word_length = len(end_tag)
    diff = len(end_tag) - len(start_tag)

    try:
        while cindex < len(html_code):
            if (cindex + word_length) > len(html_code):
                break

            word = html_code[cindex : cindex + word_length]

            if word[:-diff] == start_tag:
                if not stack:
                    sindex = cindex
                stack.append(start_tag)

            if word == end_tag:
                if len(stack) == 1:
                    eindex = cindex + word_length
                    tags.append(html_code[sindex:eindex])
                    stack = []
                elif stack:
                    stack.pop()

            cindex += 1

    except Exception as e:
        raise RecoverError(f"Failed to extract tags, error: {str(e)}") from e

    return tags
