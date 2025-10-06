from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.config import app_constants
from src.errors import AbortNteAvailableError
from src.nte.nte_available import nte_available


@pytest.fixture(autouse=True)
def _temp_data_dir(monkeypatch, tmp_path):
    original = app_constants.data_dir
    monkeypatch.setattr(app_constants, "data_dir", tmp_path, raising=False)
    yield tmp_path
    monkeypatch.setattr(app_constants, "data_dir", original, raising=False)


def test_nte_available_builds_and_uploads(monkeypatch, tmp_path):
    courses_data = {
        "1200101": {
            "Course Name": "ARCH101 - Intro",
            "Sections": {
                "1": {
                    "t": [
                        {"d": 0, "s": "09:00", "e": "10:00", "p": "R101"},
                    ],
                    "i": ["Prof"],
                    "c": [],
                },
                "2": {
                    "t": [],
                    "i": [],
                    "c": [{"d": "BLOCKED"}],
                },
            },
        },
        "1200102": {
            "Course Name": "ARCH102 - Design",
            "Sections": {
                "1": {
                    "t": [],
                    "i": [],
                    "c": [],
                }
            },
        },
    }

    departments = {
        "120": {"p": "ARCH"},
    }

    nte_list_payload = {
        "Architecture": [
            {"code": "ARCH 101", "credits": "3"},
            {"code": "ARCH 102", "credits": "4"},
            {"code": "ARCH 101", "credits": "3"},
            {"code": "", "credits": "0"},
        ]
    }

    monkeypatch.setattr("src.nte.nte_available.load_data", lambda: courses_data)
    monkeypatch.setattr("src.nte.nte_available.load_departments", lambda: departments)
    monkeypatch.setattr("src.nte.nte_available.load_nte_list", lambda: nte_list_payload)

    uploads: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "src.nte.nte_available.upload_to_s3",
        lambda path, key: uploads.append((Path(path).resolve().as_posix(), key)),
    )

    output_path_str, metrics = nte_available()
    output_path = Path(output_path_str)

    assert metrics == {"matched": 2, "missed": 1}
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    assert [course["code"]["departmental"] for course in payload] == ["ARCH101", "ARCH102"]
    assert uploads == [(output_path.resolve().as_posix(), app_constants.nte_available_json)]


def test_nte_available_raises_on_empty_output(monkeypatch):
    monkeypatch.setattr("src.nte.nte_available.load_data", lambda: {})
    monkeypatch.setattr("src.nte.nte_available.load_departments", lambda: {})
    monkeypatch.setattr("src.nte.nte_available.load_nte_list", lambda: {})

    with pytest.raises(AbortNteAvailableError) as exc:
        nte_available()

    assert "No available courses" in str(exc.value) or "No matching" in str(exc.value)
