"""HTML parsing helpers for musts pipeline."""

from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup

from app.core.errors import AppError


def extract_course_code(course_link: str | None) -> str | None:
    """Extract numeric course code from a catalog course URL."""
    try:
        if not course_link:
            return None
        parsed_url = urlparse(course_link)
        query_params = parse_qs(parsed_url.query)
        course_code = query_params.get("course_code", [None])[0]
        return course_code
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to extract course code from course link.",
            "COURSE_CODE_EXTRACTION_FAILED",
            cause=e,
        )
        raise err


def extract_dept_node(dept_soup: BeautifulSoup) -> dict[int, list[str]]:
    """Extract must-course codes grouped by semester index from department page HTML."""
    try:
        dept_node: dict[int, list[str]] = {}
        field_body = dept_soup.find("div", {"class": "field-body"})
        if field_body is None:
            raise AppError("Department page body not found.", "DEPT_BODY_NOT_FOUND")

        semester_tables = field_body.find_all("table")
        semester_tables = semester_tables[:-1]

        for sem_no, semester_table in enumerate(semester_tables, start=1):
            courses: list[str] = []
            rows = semester_table.find_all("tr")
            if not rows:
                continue
            rows = rows[1:]

            for row in rows:
                cells = row.find_all("td")
                if not cells:
                    continue
                if len(cells) != 6:
                    break

                course_link_tag = cells[0].find("a")
                if course_link_tag:
                    course_link = course_link_tag.get("href")
                    course_code = extract_course_code(course_link)
                    if course_code:
                        courses.append(course_code)

            if courses:
                dept_node[sem_no] = courses
        return dept_node
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to extract department node from HTML soup.",
            "DEPT_NODE_EXTRACTION_FAILED",
            cause=e,
        )
        raise err
