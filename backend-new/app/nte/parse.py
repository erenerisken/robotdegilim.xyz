"""Parsing helpers for NTE pipelines."""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.constants import NTE_BASE_URL
from app.core.errors import AppError

_EXTRA_DEPARTMENT_LINKS: tuple[str, str] = (
    "https://muhfd.metu.edu.tr/en/computer-education-and-instructional-technology",
    "https://muhfd.metu.edu.tr/en/meslek-yuksek-okulu-myo",
)

# NTE List parsing functions

def extract_department_links(soup: BeautifulSoup, department_links: list[str]) -> None:
    """Extract and deduplicate NTE department page links into the provided output list."""
    try:
        discovered: list[str] = []
        for anchor in soup.find_all("a"):
            href = anchor.get("href", "")
            if isinstance(href, str) and "department-" in href:
                discovered.append(urljoin(f"{NTE_BASE_URL}/en/", href))

        discovered.extend(_EXTRA_DEPARTMENT_LINKS)

        seen: set[str] = set()
        for link in discovered:
            if link and link not in seen:
                seen.add(link)
                department_links.append(link)
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to extract department links.",
            "EXTRACT_DEPARTMENT_LINKS_FAILED",
            cause=e,
        )
        raise err


def extract_courses(soup: BeautifulSoup, courses: list[dict[str, str]]) -> str:
    """Extract department name and course rows from a department page table."""
    try:
        dept_name = ""
        header_el = soup.find("h1", id="page-title")
        if header_el:
            dept_name = header_el.get_text(strip=True)

        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue
                code = cols[0].get_text(strip=True)
                name = cols[1].get_text(strip=True)
                credits = cols[2].get_text(strip=True)
                courses.append(
                    {
                        "code": code,
                        "name": name,
                        "credits": credits,
                    }
                )

        return dept_name
    except Exception as e:
        err = e if isinstance(e, AppError) else AppError(
            "Failed to extract courses from department page.",
            "NTE_EXTRACT_COURSES_FAILED",
            cause=e,
        )
        raise err
