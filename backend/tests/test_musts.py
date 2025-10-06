from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.musts.musts import run_musts


@pytest.fixture(autouse=True)
def _patch_logger(monkeypatch):
    # Silence logger noise during tests.
    monkeypatch.setattr("src.musts.musts.logger", type("Dummy", (), {"info": staticmethod(lambda *a, **k: None)})())


def test_run_musts_single_write(monkeypatch):
    departments = {
        "111": {"p": "ARCH"},
        "222": {"p": ""},
        "333": {"p": "CENG"},
    }

    responses = {
        "111": SimpleNamespace(text="a"),
        "333": SimpleNamespace(text="b"),
    }

    def fake_load_departments():
        return departments

    def fake_get_department_page(code):
        return responses[code]

    def fake_extract_dept_node(soup):
        # soup.get_text() returns the response text we provided
        return {"content": soup.get_text()}

    write_calls: list[dict] = []
    upload_calls: list[tuple[str, str]] = []

    def fake_write_musts(data):
        write_calls.append(dict(data))
        return "musts.json"

    def fake_upload(path, key):
        upload_calls.append((path, key))

    monkeypatch.setattr("src.musts.musts.load_departments", fake_load_departments)
    monkeypatch.setattr("src.musts.musts.get_department_page", fake_get_department_page)
    monkeypatch.setattr("src.musts.musts.extract_dept_node", fake_extract_dept_node)
    monkeypatch.setattr("src.musts.musts.write_musts", fake_write_musts)
    monkeypatch.setattr("src.musts.musts.upload_to_s3", fake_upload)

    run_musts()

    assert len(write_calls) == 1
    assert write_calls[0] == {
        "ARCH": {"content": "a"},
        "CENG": {"content": "b"},
    }
    assert upload_calls == [("musts.json", "musts.json")]
