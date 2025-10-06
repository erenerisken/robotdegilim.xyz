from __future__ import annotations

import pytest

from src.app import app
from src.utils.timing import set_speed_mode


@pytest.fixture
def client():
    with app.test_client() as test_client:
        set_speed_mode("normal")
        try:
            yield test_client
        finally:
            set_speed_mode("normal")


def test_speed_get_returns_current_mode(client):
    response = client.get("/speed")
    assert response.status_code == 200
    data = response.get_json()
    assert data["mode"] in {"fast", "slow", "normal"}
    assert "base_delay" in data


def test_speed_post_requires_json(client):
    response = client.post("/speed", data="mode=fast", content_type="application/x-www-form-urlencoded")
    assert response.status_code == 400


def test_speed_post_updates_mode(client):
    response = client.post("/speed", json={"mode": "fast"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["mode"] == "fast"
    assert data["base_delay"] >= 0


def test_speed_post_rejects_invalid_mode(client):
    response = client.post("/speed", json={"mode": "turbo"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["ok"] is False
    assert "error" in data
