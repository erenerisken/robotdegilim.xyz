from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup

from src.errors import RecoverError


def extract_course_code(course_link: str):
    try:
        parsed_url = urlparse(course_link)
        query_params = parse_qs(parsed_url.query)
        course_code = query_params.get("course_code", [None])[0]
        return course_code
    except Exception as e:
        raise RecoverError(
            f"Failed to extract course code: course_link: {course_link}"
        ) from e


def extract_dept_node(dept_soup: BeautifulSoup):
    dept_node = {}
    try:
        semester_tables = dept_soup.find("div", {"class": "field-body"}).find_all("table")
        semester_tables = semester_tables[:-1]

        for sem_no, semester_table in enumerate(semester_tables, start=1):
            courses = []
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

                course_link = cells[0].find("a")
                if course_link:
                    course_link = course_link.get("href")
                    course_code = extract_course_code(course_link)
                    if course_code:
                        courses.append(course_code)

            if courses:
                dept_node[sem_no] = courses
    except Exception as e:
        raise RecoverError("Failed to extract the node") from e
    return dept_node
