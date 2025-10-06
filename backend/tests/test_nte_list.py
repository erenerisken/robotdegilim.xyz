from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.config import app_constants
from src.nte.nte_list import nte_list


@pytest.fixture(autouse=True)
def _temp_data_dir(monkeypatch, tmp_path):
    original = app_constants.data_dir
    monkeypatch.setattr(app_constants, "data_dir", tmp_path, raising=False)
    yield tmp_path
    monkeypatch.setattr(app_constants, "data_dir", original, raising=False)


def test_nte_list_deduplicates_links_and_publishes(monkeypatch, tmp_path):
    departments_payload = {
        "link-a": (
            "Architecture",
            [
                {"code": "ARCH 101", "name": "Intro", "credits": "3"},
                {"code": "ARCH 101", "name": "Intro", "credits": "3"},
            ],
        ),
        "link-b": (
            "Computer Engineering",
            [
                {"code": "CENG 201", "name": "Data", "credits": "4"},
            ],
        ),
    }

    def fake_extract_department_links(_soup, dest):
        dest.extend(["link-a", "link-a", "link-b"])

    def fake_get_department_data(link):
        return SimpleNamespace(text=link)

    def fake_extract_courses(soup, courses):
        dept_name, dept_courses = departments_payload.get(soup.text, ("", []))
        courses.extend(dept_courses)
        return dept_name

    upload_calls: list[tuple[str, str]] = []

    monkeypatch.setattr("src.nte.nte_list.extract_department_links", fake_extract_department_links)
    monkeypatch.setattr("src.nte.nte_list.get_nte_courses", lambda: SimpleNamespace(text=""))
    monkeypatch.setattr("src.nte.nte_list.get_department_data", fake_get_department_data)
    monkeypatch.setattr("src.nte.nte_list.extract_courses", fake_extract_courses)
    monkeypatch.setattr(
        "src.nte.nte_list.upload_to_s3",
        lambda path, key: upload_calls.append((Path(path).resolve().as_posix(), key)),
    )

    output_path = Path(nte_list())
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    assert set(data.keys()) == {"Architecture", "Computer Engineering"}
    assert data["Architecture"] == [{"code": "ARCH 101", "name": "Intro", "credits": "3"}]
    assert data["Computer Engineering"] == [
        {"code": "CENG 201", "name": "Data", "credits": "4"}
    ]

    assert upload_calls == [(output_path.resolve().as_posix(), app_constants.nte_list_json)]
