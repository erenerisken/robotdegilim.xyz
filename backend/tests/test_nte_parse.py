"""Unit tests for NTE parse helpers."""

from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from app.core.errors import AppError
from app.nte.parse import (
    build_available_index,
    build_course_output,
    extract_courses,
    extract_department_links,
    extract_nte_courses,
)


class NteParseTests(unittest.TestCase):
    """Validate NTE parse helpers for list and available pipelines."""

    def test_extract_department_links_deduplicates_and_adds_extra(self) -> None:
        """Department links should be deduplicated and include extra configured links."""
        html = """
        <html>
          <body>
            <a href="/en/department-architecture">Architecture</a>
            <a href="/en/department-architecture">Architecture duplicate</a>
            <a href="/en/department-physics">Physics</a>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        links: list[str] = []

        extract_department_links(soup, links)

        self.assertIn("https://muhfd.metu.edu.tr/en/department-architecture", links)
        self.assertIn("https://muhfd.metu.edu.tr/en/department-physics", links)
        self.assertIn("https://muhfd.metu.edu.tr/en/computer-education-and-instructional-technology", links)
        self.assertEqual(len(links), len(set(links)))

    def test_extract_courses_reads_h1_and_table_rows(self) -> None:
        """extract_courses should parse department title and table entries."""
        html = """
        <html>
          <h1>Department of Test</h1>
          <table>
            <tr><th>Code</th><th>Name</th><th>Credits</th></tr>
            <tr><td>CENG 101</td><td>Intro</td><td>4</td></tr>
            <tr><td>CENG 102</td><td>Data</td><td>3</td></tr>
          </table>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        courses: list[dict[str, str]] = []

        dept_name = extract_courses(soup, courses)

        self.assertEqual(dept_name, "Department of Test")
        self.assertEqual(len(courses), 2)
        self.assertEqual(courses[0]["code"], "CENG 101")
        self.assertEqual(courses[1]["name"], "Data")

    def test_extract_nte_courses_deduplicates_by_normalized_code(self) -> None:
        """NTE courses should be flattened and deduplicated by normalized code."""
        nte_data = {
            "DeptA": [{"code": "CENG 101", "name": "Intro", "credits": "4"}],
            "DeptB": [{"code": "CENG101", "name": "Intro duplicate", "credits": "4"}],
        }
        output: list[dict[str, str]] = []

        extract_nte_courses(nte_data, output)

        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]["code"], "CENG 101")

    def test_extract_nte_courses_empty_raises_no_courses_error(self) -> None:
        """Empty extracted list should raise explicit no-courses AppError."""
        with self.assertRaises(AppError) as exc:
            extract_nte_courses({"X": []}, [])
        self.assertEqual(exc.exception.code, "NTE_AVAILABLE_NO_NTE_COURSES")

    def test_build_available_index_filters_constraints_and_prefixes(self) -> None:
        """Available index should include only available sections with valid department prefix."""
        courses = {
            "571101": {
                "Course Name": "Intro",
                "Sections": {
                    "1": {"c": [], "t": [], "i": []},  # available (no constraints)
                },
            },
            "999101": {
                "Course Name": "No Prefix",
                "Sections": {"1": {"c": [], "t": [], "i": []}},
            },
            "571102": {
                "Course Name": "Blocked",
                "Sections": {
                    "1": {"c": [{"d": "SOME OTHER"}], "t": [], "i": []},  # not available
                },
            },
        }
        dept_map = {
            "571": {"p": "CENG"},
            "999": {"p": "<prefix-not-found>"},
        }

        index = build_available_index(courses, dept_map)

        self.assertIn("CENG101", index)
        self.assertNotIn("999101", index)
        self.assertEqual(index["CENG101"]["numeric"], "571101")
        self.assertEqual(index["CENG101"]["name"], "Intro")

    def test_build_course_output_includes_only_available_sections(self) -> None:
        """Course output should keep available sections and map day indexes to labels."""
        courses_data = {
            "571101": {
                "Sections": {
                    "1": {
                        "c": [],
                        "t": [{"d": 0, "s": "08:40", "e": "09:30", "p": "BMB1"}],
                        "i": ["Prof A"],
                    },
                    "2": {
                        "c": [{"d": "ONLY EE"}],  # unavailable
                        "t": [{"d": 1, "s": "10:00", "e": "11:00", "p": "BMB2"}],
                        "i": ["Prof B"],
                    },
                }
            }
        }

        output = build_course_output(
            course_code="571101",
            prefixed_code="CENG 101",
            course_name="Intro",
            credits="4",
            courses_data=courses_data,
        )

        self.assertEqual(output["code"]["departmental"], "CENG 101")
        self.assertEqual(len(output["sections"]), 1)
        self.assertEqual(output["sections"][0]["section_id"], "1")
        self.assertEqual(output["sections"][0]["times"][0]["day"], "Monday")
        self.assertEqual(output["sections"][0]["instructors"], ["Prof A"])

    def test_build_course_output_falls_back_when_no_available_section(self) -> None:
        """When no available section exists, output should include fallback section entry."""
        courses_data = {
            "571101": {
                "Sections": {
                    "1": {"c": [{"d": "ONLY EE"}], "t": [], "i": []},
                }
            }
        }

        output = build_course_output(
            course_code="571101",
            prefixed_code="CENG 101",
            course_name="Intro",
            credits="4",
            courses_data=courses_data,
        )

        self.assertEqual(output["sections"][0]["section_id"], "not found")
        self.assertEqual(output["sections"][0]["times"][0]["day"], "No Timestamp Added Yet")


if __name__ == "__main__":
    unittest.main()
