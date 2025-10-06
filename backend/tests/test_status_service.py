from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from src.config import app_constants
from src.services import status_service


@pytest.fixture(autouse=True)
def _temp_data_dir(monkeypatch, tmp_path):
    original_dir = app_constants.data_dir
    monkeypatch.setattr(app_constants, "data_dir", tmp_path, raising=False)
    yield tmp_path
    monkeypatch.setattr(app_constants, "data_dir", original_dir, raising=False)


def test_get_status_defaults_when_s3_fails(monkeypatch):
    class BrokenClient:
        def get_object(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:  # pragma: no cover - stub
            raise RuntimeError("boom")

    monkeypatch.setattr(status_service, "get_s3_client", lambda: BrokenClient())

    result = status_service.get_status()

    assert result["status"] == "idle"
    assert result["queued_musts"] is False
    assert result["depts_ready"] is False


def test_set_status_writes_file_and_uploads(monkeypatch, tmp_path):
    base_state = {"status": "idle", "queued_musts": False, "depts_ready": False}
    monkeypatch.setattr(status_service, "get_status", lambda: dict(base_state))

    uploads: list[tuple[str, str]] = []
    monkeypatch.setattr(status_service, "upload_to_s3", lambda path, key: uploads.append((path, key)))

    updated = status_service.set_status(status="busy", queued_musts=True)

    assert updated["status"] == "busy"
    assert updated["queued_musts"] is True

    status_path = Path(tmp_path) / app_constants.status_json
    assert status_path.exists()
    data = json.loads(status_path.read_text())
    assert data["status"] == "busy"
    assert data["queued_musts"] is True

    assert uploads, "upload_to_s3 should be called"
    assert Path(uploads[0][0]) == status_path
    assert uploads[0][1] == app_constants.status_json


def test_detect_depts_ready_prefers_local_file(monkeypatch, tmp_path):
    departments_path = Path(tmp_path) / app_constants.departments_json
    departments_path.write_text(json.dumps({"123": {"n": "Dept", "p": "DEP"}}))

    # Ensure S3 is not consulted if local file exists by raising if accessed
    def _fail_get_s3_client():  # pragma: no cover - guard
        raise AssertionError("S3 should not be queried when local cache exists")

    monkeypatch.setattr(status_service, "get_s3_client", _fail_get_s3_client)

    assert status_service.detect_depts_ready() is True


def test_detect_depts_ready_falls_back_to_s3(monkeypatch, tmp_path):
    class DummyClient:
        def head_object(self, *, Bucket: str, Key: str) -> None:  # pragma: no cover - stub
            assert Bucket == app_constants.s3_bucket_name
            assert Key == app_constants.departments_json

    monkeypatch.setattr(status_service, "get_s3_client", lambda: DummyClient())

    assert status_service.detect_depts_ready() is True