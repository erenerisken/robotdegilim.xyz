"""HTML parsing helpers for scrape pipeline extraction stages."""

import logging
from typing import Any, cast

from bs4 import BeautifulSoup
from bs4.element import Tag

from app.core.constants import DAYS_MAP
from app.core.errors import AppError
from app.core.logging import log_item
from app.scrape.fetch import get_section_page


def _strip_upper(s: Any) -> str:
    """Normalize string-like values by stripping and upper-casing."""
    return str(s or "").strip().upper()


def extract_departments(
    soup: BeautifulSoup, dept_codes: list[str], dept_names: dict[str, str]
) -> None:
    """Extract department codes and names from the main page."""
    try:
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
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to extract departments", "EXTRACT_DEPARTMENTS_FAILED", cause=e)
        raise err


def extract_current_semester(soup: BeautifulSoup) -> tuple[str, str]:
    """Extract current semester code and label from the main page."""
    try:
        semester_select = soup.find("select", {"name": "select_semester"})
        if semester_select:
            current_semester_option = semester_select.find("option")
            if current_semester_option:
                value = _strip_upper(current_semester_option.get("value"))
                text = (current_semester_option.get_text() or "").strip()
                return (value, text)
        raise AppError("Extracting current semester failed", "EXTRACT_CURRENT_SEMESTER_FAILED")
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to extract current semester", "EXTRACT_CURRENT_SEMESTER_FAILED", cause=e)
        raise err


def extract_courses(
    soup: BeautifulSoup, course_codes: list[str], course_names: dict[str, str]
) -> None:
    """Extract course codes and names from department page table."""
    try:
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
                    if course_cells and len(course_cells) >= 3 and course_cells[0].find("input"):
                        course_code = course_cells[0].find("input").get("value")
                        course_name = course_cells[2].get_text()
                        if course_code and course_name:
                            course_code = _strip_upper(course_code)
                            course_name = (course_name or "").strip()
                            course_codes.append(course_code)
                            course_names[course_code] = course_name
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to extract courses", "EXTRACT_COURSES_FAILED", cause=e)
        raise err


def extract_sections(cache: Any, soup: BeautifulSoup, sections: dict[str, dict[str, Any]]) -> None:
    """Extract sections, constraints, and time slots from a course detail page."""
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
            section_node: dict[str, Any] = {}

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
                if len(time_cells) < 4:
                    continue
                if (
                    not time_cells[0].get_text()
                    or time_cells[0].get_text() not in DAYS_MAP
                ):
                    continue
                section_times.append(
                    {
                        "p": time_cells[3].find("font").get_text(),
                        "s": time_cells[1].find("font").get_text(),
                        "e": time_cells[2].find("font").get_text(),
                        "d": DAYS_MAP[time_cells[0].get_text()],
                    }
                )

            section_input = info_cells[0].find("input") if info_cells else None
            section_code = section_input.get("value") if section_input else None
            if not section_code:
                continue
            section_instructors = [info_cells[1].get_text(), info_cells[2].get_text()]
            cache_key, html_hash, response = get_section_page(section_code)
            parsed = cache.get(cache_key, html_hash)

            section_constraints = []
            if parsed:
                section_constraints = parsed["section_constraints"]
            else:
                section_soup = BeautifulSoup(response.text, "html.parser")
                form_msg_node = section_soup.find("div", id="formmessage")
                form_msg = form_msg_node.find("b").get_text() if form_msg_node and form_msg_node.find("b") else ""
                if not form_msg:
                    extract_constraints(section_soup, section_constraints)
                cache.set(
                    cache_key,
                    html_hash,
                    {"section_constraints": section_constraints},
                )

            section_node["i"] = section_instructors
            section_node["c"] = section_constraints
            section_node["t"] = section_times
            sections[section_code] = section_node

    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to extract sections", "EXTRACT_SECTIONS_FAILED", cause=e)
        raise err


def extract_constraints(soup: BeautifulSoup, constraints: list[dict[str, str]]) -> None:
    """Extract section constraints table rows."""
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
        err = e if isinstance(e, AppError) else AppError("Failed to extract constraints", "EXTRACT_CONSTRAINTS_FAILED", cause=e)
        raise err


def any_course(soup: BeautifulSoup) -> bool:
    """Return False when form message indicates no courses for department."""
    try:
        form_msg_node = soup.find("div", id="formmessage")
        form_msg = form_msg_node.find("b").get_text() if form_msg_node and form_msg_node.find("b") else ""
        if form_msg:
            return False
        return True
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to determine if any course exists", "ANY_COURSE_FAILED", cause=e)
        raise err


def deptify(prefix: str, course_code: str) -> str:
    """Build prefixed human-readable course code from numeric code."""
    try:
        result = "" + prefix
        if len(course_code) > 4 and course_code[3] == "0":
            result += course_code[4:]
        else:
            result += course_code[3:]
        return result
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to deptify course code", "DEPTIFY_FAILED", cause=e)
        raise err


def extract_tags_as_string(html_code: str, start_tag: str, end_tag: str) -> list[str]:
    """Extract nested HTML tag blocks as strings using stack matching."""
    try:
        stack: list[str] = []
        tags: list[str] = []
        sindex = 0
        cindex = 0
        word_length = len(end_tag)
        diff = len(end_tag) - len(start_tag)

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
        return tags
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError("Failed to extract tags as string", "EXTRACT_TAGS_AS_STRING_FAILED", cause=e)
        raise err


def extract_dept_prefix(catalog_soup: BeautifulSoup) -> str | None:
    """Extract alphabetic department prefix from catalog page heading."""
    try:
        h2 = catalog_soup.find("h2")
        if h2 is None:
            return None
        course_code_with_prefix = h2.get_text().split(" ")[0]
        dept_prefix = "".join([char for char in course_code_with_prefix if char.isalpha()])
        if dept_prefix:
            return dept_prefix
        return None
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            message="Failed to extract department prefix",
            code="EXTRACT_DEPT_PREFIX_FAILED",
            cause=e,
        )
        log_item("scrape", logging.WARNING, err)
        return None
