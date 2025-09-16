"""Local debug helper for running musts with optional mocks.

How to use:
- Preferred: import and call run_debug() from app.py's __main__ block.
    app.py should handle serving the Flask app; this helper will only run musts.
- Or run directly: `python -m src.debug_helper` (runs run_musts once).

Edit constants inside run_debug() to control behavior. This module is never
imported in production unless you explicitly do so.
"""

from __future__ import annotations

import logging
from pathlib import Path
import sys
import time
from typing import Iterable, Dict, Optional, Tuple, List
from contextlib import contextmanager
from unittest.mock import patch, _patch


class Step:
    """Lightweight timing/logging context for clearer debug flow."""

    def __init__(self, name: str):
        self.name = name
        self.t0 = 0.0
        self.log = logging.getLogger(__name__)

    def __enter__(self):
        self.t0 = time.time()
        self.log.info(f"▶ {self.name}...")
        return self

    def __exit__(self, exc_type, exc, tb):
        dt = (time.time() - self.t0) * 1000
        if exc:
            self.log.error(f"✖ {self.name} failed after {dt:.0f} ms: {exc}")
        else:
            self.log.info(f"✔ {self.name} done in {dt:.0f} ms")


def ensure_backend_on_path() -> Path:
    """Ensure backend root is on sys.path for `src.*` imports and return it."""
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    return backend_root


def load_backend_env(backend_root: Path) -> None:
    """Load backend/.env if python-dotenv is available."""
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv(backend_root / ".env")
    except Exception:
        pass


def setup_console_logging(log_level: int, console_log: bool, http_debug: bool, _C) -> None:
    if not console_log:
        return
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    for name in (
        _C.log_parent,
        _C.log_app,
        _C.log_scrape,
        _C.log_musts,
        _C.log_utils,
    ):
        lg = logging.getLogger(name)
        lg.setLevel(log_level)
        if not any(isinstance(h, logging.StreamHandler) for h in lg.handlers):
            sh = logging.StreamHandler()
            sh.setLevel(log_level)
            sh.setFormatter(fmt)
            lg.addHandler(sh)
    if http_debug:
        for name in ("urllib3", "requests"):
            log = logging.getLogger(name)
            log.setLevel(logging.DEBUG)
            if not any(isinstance(h, logging.StreamHandler) for h in log.handlers):
                log.addHandler(logging.StreamHandler())


def dump_config(cfg: Dict[str, object]) -> None:
    lines = ["Debug run configuration:"] + [f"  {k:<11}= {v}" for k, v in cfg.items()]
    logging.getLogger(__name__).info("\n" + "\n".join(lines))


@contextmanager
def null_cm():
    yield


def make_s3_patches() -> Tuple[_patch, _patch, _patch, _patch]:
    """Return patches to mock S3 client, idle state, uploads, and busy/idle ctx."""
    return (
        patch("src.utils.s3.get_s3_client", lambda: None),
        patch("src.utils.s3.is_idle", lambda _s3: True),
        patch("src.utils.s3.upload_to_s3", lambda *_a, **_k: None),
        patch("src.utils.run.busy_idle", lambda _s3: null_cm()),
    )


def preflight_departments_info() -> Optional[Dict[str, object]]:
    try:
        import src.musts.io as _musts_io  # noqa: F401
        pre = _musts_io.load_departments()
        return {
            "total": len(pre or {}),
            "sample": list((pre or {}).keys())[:5],
        }
    except Exception:
        return None


def limit_departments_wrapper(orig_func, dept_limit: Optional[int], select_depts: Optional[Iterable[str]]):
    def wrapper():
        data = orig_func()
        if not data:
            return data
        if select_depts:
            return {k: v for k, v in data.items() if k in select_depts}
        if dept_limit is None:
            return data
        limited = {}
        for idx, k in enumerate(data.keys()):
            if idx >= int(dept_limit):
                break
            limited[k] = data[k]
        return limited
    return wrapper


def make_limit_patch(dept_limit: Optional[int], select_depts: Optional[Iterable[str]]) -> Optional[_patch]:
    if dept_limit is None and not select_depts:
        return None
    try:
        import src.musts.io as _musts_io
        return patch("src.musts.io.load_departments", limit_departments_wrapper(_musts_io.load_departments, dept_limit, select_depts))
    except Exception:
        return None


def tap_department_page_wrapper(_C, orig_func):
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


def make_html_patch(save_html: bool, _C) -> Optional[_patch]:
    if not save_html:
        return None
    try:
        import src.musts.fetch as _musts_fetch
        return patch("src.musts.fetch.get_department_page", tap_department_page_wrapper(_C, _musts_fetch.get_department_page))
    except Exception:
        return None


def make_write_patch(dry_write: bool, _C) -> Optional[_patch]:
    if not dry_write:
        return None
    try:
        import json
        import src.musts.io as _musts_io  # noqa: F401

        def _write_debug(musts_data):
            out = _C.data_dir / "musts.debug.json"
            out.write_text(json.dumps(musts_data, ensure_ascii=False, indent=2), encoding="utf-8")
            logging.getLogger(__name__).info(f"DRY_WRITE: wrote debug output to {out}")

        return patch("src.musts.io.write_musts", _write_debug)
    except Exception:
        return None


def apply_patches(patches: Iterable[Optional[_patch]]) -> List[_patch]:
    started: List[_patch] = []
    for p in patches:
        if p is None:
            continue
        p.start()
        started.append(p)
    return started


def stop_patches(started: Iterable[_patch]) -> None:
    for p in reversed(list(started)):
        try:
            p.stop()
        except Exception:
            pass


def run_debug():
    """Run local musts debug flow without external args.

    Flip constants below to control behavior. Safe for local use; does not
    affect production imports. Note: This helper does NOT start the Flask
    server; app.py is responsible for serving the API.
    """
    # Prepare import path and env
    _BACKEND_ROOT = ensure_backend_on_path()
    load_backend_env(_BACKEND_ROOT)

    # Toggles
    RUN_MUSTS = True         # True: run run_musts() once; False: no-op
    MOCK_S3 = True           # True: bypass S3 (idle + no uploads)
    LOG_LEVEL = logging.DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    CONSOLE_LOG = True       # True: show logs in terminal
    SPEED_MODE = "fast"      # "fast" | "normal" | "slow"
    DEPT_LIMIT = 5           # int or None; limits departments processed
    SAVE_HTML = False        # True: save fetched department HTML under data/debug_html
    SELECT_DEPTS: Iterable[str] | None = None  # e.g., ("CENG", "EE")
    HTTP_DEBUG = False       # True: enable urllib3/requests debug logs
    DRY_WRITE = False        # True: write output to musts.debug.json instead of normal path

    # Local imports to avoid affecting production module import time
    from src.config import app_constants as _C
    from src.utils.timing import set_speed_mode as _set_speed_mode
    # Delay importing run_musts until after optional patches are set up
    # to minimize any side effects during import

    # Console logging
    setup_console_logging(LOG_LEVEL, CONSOLE_LOG, HTTP_DEBUG, _C)

    # Banner + config dump
    dump_config({
        "RUN_MUSTS": RUN_MUSTS,
        "MOCK_S3": MOCK_S3,
        "SPEED_MODE": SPEED_MODE,
        "DEPT_LIMIT": DEPT_LIMIT,
        "SELECT_DEPTS": list(SELECT_DEPTS) if SELECT_DEPTS else None,
        "SAVE_HTML": SAVE_HTML,
        "DRY_WRITE": DRY_WRITE,
        "HTTP_DEBUG": HTTP_DEBUG,
    })

    # Speed mode for throttling
    with Step("Set speed mode"):
        try:
            state = _set_speed_mode(SPEED_MODE)
            logging.getLogger(__name__).info(f"Speed state: {state}")
        except Exception:
            pass

    # Optional: Mock S3 to avoid AWS creds and uploads
    s3_patches = make_s3_patches()

    # Preflight: peek current departments before patching, for context
    pre_dept_info: Dict[str, object] | None = preflight_departments_info()
    if pre_dept_info:
        logging.getLogger(__name__).info(
            f"Departments available before patching: total={pre_dept_info['total']} sample={pre_dept_info['sample']}"
        )

    # Optional: Limit/filter departments to a subset
    limit_patch = make_limit_patch(DEPT_LIMIT, SELECT_DEPTS)

    # Optional: Save HTML of fetched departments
    html_patch = make_html_patch(SAVE_HTML, _C)

    # Optional: redirect write_musts to a debug path to avoid overwriting production outputs
    write_patch = make_write_patch(DRY_WRITE, _C)

    # Apply patches
    started: List[_patch] = []
    try:
        with Step("Apply debug patches"):
            if MOCK_S3:
                started.extend(apply_patches(s3_patches))
            started.extend(apply_patches([limit_patch, html_patch, write_patch]))

        # Import run_musts only after patches are active
        from src.musts.musts import run_musts as _run_musts

        if RUN_MUSTS:
            with Step("Execute run_musts"):
                t0 = time.time()
                result = _run_musts()
                dt = (time.time() - t0) * 1000
                logging.getLogger(__name__).info(f"run_musts() -> {result} in {dt:.0f} ms")
        else:
            logging.getLogger(__name__).info("RUN_MUSTS is False; nothing to run.")
    finally:
        stop_patches(started)


if __name__ == "__main__":
    # Allow running this helper directly: `python -m src.debug_helper`
    run_debug()
