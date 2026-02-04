"""Build a Fly.io deploy-ready folder from backend sources."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _repo_backend_root() -> Path:
    """Return backend root directory for this script."""
    return Path(__file__).resolve().parents[1]


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    backend_root = _repo_backend_root()
    parser = argparse.ArgumentParser(description="Create Fly.io deploy folder from backend sources.")
    parser.add_argument(
        "--out",
        type=Path,
        default=backend_root / ".deploy" / "fly",
        help="Output deploy directory (default: backend/.deploy/fly)",
    )
    parser.add_argument(
        "--app-name",
        type=str,
        default="robotdegilim-backend",
        help="Fly application name used in generated fly.toml.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        default=True,
        help="Remove output directory before rebuild (default: true).",
    )
    parser.add_argument(
        "--no-clean",
        action="store_false",
        dest="clean",
        help="Do not remove output directory before rebuild.",
    )
    return parser.parse_args()


def _assert_required_inputs(backend_root: Path) -> None:
    """Fail fast when mandatory source files are missing."""
    required = [
        backend_root / "app" / "main.py",
        backend_root / "requirements.txt",
        backend_root / ".env",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required source files: {', '.join(missing)}")


def _ignore_copy_patterns(_: str, names: list[str]) -> set[str]:
    """Ignore transient Python/runtime artifacts while copying."""
    ignored: set[str] = set()
    for name in names:
        if name in {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"}:
            ignored.add(name)
        elif name.endswith((".pyc", ".pyo", ".pyd")):
            ignored.add(name)
    return ignored


def _copy_core_sources(backend_root: Path, out_dir: Path) -> list[str]:
    """Copy required backend sources into deploy directory."""
    copied: list[str] = []

    app_src = backend_root / "app"
    app_dst = out_dir / "app"
    shutil.copytree(app_src, app_dst, dirs_exist_ok=True, ignore=_ignore_copy_patterns)
    copied.append("app/**")

    for file_name in ("requirements.txt", ".env", ".env.example"):
        src = backend_root / file_name
        if src.exists():
            shutil.copy2(src, out_dir / file_name)
            copied.append(file_name)

    raw_src = backend_root / "data" / "raw"
    raw_dst = out_dir / "data" / "raw"
    raw_dst.mkdir(parents=True, exist_ok=True)
    if raw_src.exists():
        shutil.copytree(raw_src, raw_dst, dirs_exist_ok=True, ignore=_ignore_copy_patterns)
    copied.append("data/raw/**")

    return copied


def _create_required_empty_dirs(out_dir: Path) -> list[str]:
    """Create runtime directories that must exist but stay empty."""
    rel_dirs = [
        "data/cache",
        "data/downloaded",
        "data/logs",
        "data/published",
        "data/staged",
        "s3-mock",
    ]
    for rel in rel_dirs:
        (out_dir / rel).mkdir(parents=True, exist_ok=True)
    return rel_dirs


def _build_dockerfile(app_name: str) -> str:
    """Return Dockerfile content for production deployment."""
    workdir = f"/{app_name.strip()}" if app_name.strip() else "/app"
    return "\n".join(
        [
            "FROM python:3.12-slim",
            "",
            "ENV PYTHONDONTWRITEBYTECODE=1",
            "ENV PYTHONUNBUFFERED=1",
            "",
            f"WORKDIR {workdir}",
            "",
            "COPY requirements.txt ./",
            "RUN pip install --no-cache-dir -r requirements.txt",
            "",
            "COPY . .",
            "",
            "EXPOSE 8000",
            'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]',
            "",
        ]
    )


def _build_fly_toml(app_name: str) -> str:
    """Return fly.toml content."""
    return "\n".join(
        [
            f'app = "{app_name}"',
            "",
            "[http_service]",
            "  internal_port = 8000",
            "  force_https = true",
            '  auto_stop_machines = "off"',
            "  auto_start_machines = false",
            "  min_machines_running = 1",
            '  processes = ["app"]',
            "",
        ]
    )


def _build_dockerignore(backend_root: Path) -> str:
    """Build deploy .dockerignore from backend .gitignore plus deploy-safe overrides."""
    gitignore_path = backend_root / ".gitignore"
    lines: list[str] = []
    if gitignore_path.exists():
        lines.extend(gitignore_path.read_text(encoding="utf-8").splitlines())

    lines.extend(
        [
            "",
            "# Deploy-safe overrides",
            ".venv/",
            "tests/",
            "__pycache__/",
            "*.py[cod]",
            "*.pyc",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            "!.env",
            "",
            "# Keep raw data, ignore other runtime data files",
            "data/*",
            "!data/raw/",
            "!data/raw/**",
            "!data/cache/",
            "data/cache/*",
            "!data/downloaded/",
            "data/downloaded/*",
            "!data/logs/",
            "data/logs/*",
            "!data/published/",
            "data/published/*",
            "!data/staged/",
            "data/staged/*",
            "",
            "s3-mock/*",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_generated_files(out_dir: Path, app_name: str, backend_root: Path) -> list[str]:
    """Write generated deployment artifacts."""
    generated = {
        "Dockerfile": _build_dockerfile(app_name),
        "fly.toml": _build_fly_toml(app_name),
        ".dockerignore": _build_dockerignore(backend_root),
    }
    for name, content in generated.items():
        (out_dir / name).write_text(content, encoding="utf-8")
    return list(generated.keys())


def _validate_output(out_dir: Path) -> None:
    """Ensure deploy folder includes mandatory files and folders."""
    required = [
        out_dir / "app" / "main.py",
        out_dir / "requirements.txt",
        out_dir / ".env",
        out_dir / "data" / "raw",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Deploy folder validation failed. Missing: {', '.join(missing)}")


def main() -> None:
    """Build deploy-ready folder and print a summary."""
    args = _parse_args()
    backend_root = _repo_backend_root()
    out_dir = args.out.resolve()

    _assert_required_inputs(backend_root)

    if args.clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    copied = _copy_core_sources(backend_root, out_dir)
    created_dirs = _create_required_empty_dirs(out_dir)
    generated = _write_generated_files(out_dir, args.app_name, backend_root)
    _validate_output(out_dir)

    print("Fly deploy folder created successfully.")
    print(f"Output: {out_dir}")
    print("Copied:")
    for item in copied:
        print(f"  - {item}")
    print("Created empty dirs:")
    for item in created_dirs:
        print(f"  - {item}")
    print("Generated:")
    for item in generated:
        print(f"  - {item}")
    print("Next:")
    print(f"  cd {out_dir}")
    print("  fly deploy")


if __name__ == "__main__":
    main()
