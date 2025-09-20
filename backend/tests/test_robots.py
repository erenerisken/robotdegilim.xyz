import os
import importlib

# Ensure config static_folder points to existing directory
from src.config import app_constants

def test_static_folder_exists():
    assert app_constants.static_folder.exists(), f"Static folder missing: {app_constants.static_folder}"
    assert (app_constants.static_folder / 'robots.txt').exists(), "robots.txt not found in static folder"


def test_robots_served():
    from src.app import app  # import after config check
    client = app.test_client()
    resp = client.get('/robots.txt')
    assert resp.status_code == 200, f"Expected 200 got {resp.status_code} body={resp.data!r}"
    assert b'User-agent' in resp.data
