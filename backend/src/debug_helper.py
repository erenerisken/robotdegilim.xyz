"""Local debug helper for running musts or serving API with optional mocks.

Edit constants inside run_debug() to control behavior. This file is imported
nowhere in production unless you explicitly import and call run_debug() from
app.py's __main__ block.
"""

from __future__ import annotations

import logging
from pathlib import Path
import sys


def run_debug():
    """Run local debug flow without external args.

    Flip constants below to control behavior. Safe for local use; does not
    affect production imports.
    """
    # Ensure absolute imports like `from src.*` work if this is run directly
    _BACKEND_ROOT = Path(__file__).resolve().parents[1]
    if str(_BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(_BACKEND_ROOT))

    # Toggles
    RUN_MUSTS = True         # True: run run_musts() once; False: serve Flask
    MOCK_S3 = True           # True: bypass S3 (idle + no uploads)
    LOG_LEVEL = logging.DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    CONSOLE_LOG = True       # True: show logs in terminal
    SPEED_MODE = "fast"      # "fast" | "normal" | "slow"
    DEPT_LIMIT = 5           # int or None; limits departments processed
    SAVE_HTML = False        # True: save fetched department HTML under data/debug_html

    # Local imports to avoid affecting production module import time
    from contextlib import contextmanager
    from unittest.mock import patch
    from src.musts.musts import run_musts as _run_musts
    from src.config import app_constants as _C
    from src.utils.timing import set_speed_mode as _set_speed_mode
    from src.app import app  # reuse the Flask app instance

    # Console logging
    if CONSOLE_LOG:
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        for name in (
            _C.log_parent,
            _C.log_app,
            _C.log_scrape,
            _C.log_musts,
            _C.log_utils,
        ):
            lg = logging.getLogger(name)
            if not any(isinstance(h, logging.StreamHandler) for h in lg.handlers):
                sh = logging.StreamHandler()
                sh.setLevel(LOG_LEVEL)
                sh.setFormatter(fmt)
                lg.addHandler(sh)

    # Speed mode for throttling
    try:
        _set_speed_mode(SPEED_MODE)
    except Exception:
        pass

    @contextmanager
    def _null_cm():
        yield

    # Optional: Mock S3 to avoid AWS creds and uploads
    s3_patches = (
        patch("src.utils.s3.get_s3_client", lambda: None),
        patch("src.utils.s3.is_idle", lambda _s3: True),
        patch("src.utils.s3.upload_to_s3", lambda *_a, **_k: None),
        patch("src.utils.run.busy_idle", lambda _s3: _null_cm()),
    )

    # Optional: Limit departments to a small subset
    def _limit_departments(orig_func):
        def wrapper():
            data = orig_func()
            if not data or DEPT_LIMIT is None:
                return data
            limited = {}
            for idx, k in enumerate(data.keys()):
                if idx >= int(DEPT_LIMIT):
                    break
                limited[k] = data[k]
            return limited
        return wrapper

    limit_patch = patch("src.musts.io.load_departments")
    limit_active = False
    try:
        if DEPT_LIMIT is not None:
            import src.musts.io as _musts_io
            limit_patch = patch(
                "src.musts.io.load_departments", _limit_departments(_musts_io.load_departments)
            )
            limit_active = True
    except Exception:
        pass

    # Optional: Save HTML of fetched departments
    def _tap_department_page(orig_func):
        def wrapper(session, dept_code, *a, **k):
            resp = orig_func(session, dept_code, *a, **k)
            try:
                out_dir = _C.data_dir / "debug_html"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"{dept_code}.html").write_text(resp.text, encoding="utf-8")
            except Exception:
                pass
            return resp
        return wrapper

    html_patch = patch("src.musts.fetch.get_department_page")
    html_active = False
    try:
        if SAVE_HTML:
            import src.musts.fetch as _musts_fetch
            html_patch = patch(
                "src.musts.fetch.get_department_page",
                _tap_department_page(_musts_fetch.get_department_page),
            )
            html_active = True
    except Exception:
        pass

    # Apply patches
    started = []
    try:
        if MOCK_S3:
            for p in s3_patches:
                p.start(); started.append(p)
        if limit_active:
            limit_patch.start(); started.append(limit_patch)
        if html_active:
            html_patch.start(); started.append(html_patch)

        if RUN_MUSTS:
            result = _run_musts()
            print("run_musts() ->", result)
        else:
            # Serve Flask app for API testing
            app.run(host="localhost", port=5000, debug=True)
    finally:
        for p in reversed(started):
            try:
                p.stop()
            except Exception:
                pass
