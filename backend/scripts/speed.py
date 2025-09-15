"""
Small helper to read or set backend speed mode via /speed endpoint.

Usage:
  python scripts/speed.py                 # GET current mode
  python scripts/speed.py fast            # set fast
  python scripts/speed.py slow            # set slow
  python scripts/speed.py normal          # reset to normal
  python scripts/speed.py --base-url URL  # override base URL (default http://localhost:3000)

Optionally set BACKEND_URL env var to change the default base URL.
"""
from __future__ import annotations

import argparse
import os
import sys
import json
import requests


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Toggle backend speed mode")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["fast", "slow", "normal"],
        help="Desired mode. Omit to fetch current state.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("BACKEND_URL", "http://localhost:3000"),
        help="Backend base URL (default: http://localhost:3000 or BACKEND_URL env)",
    )
    args = parser.parse_args(argv)

    url = args.base_url.rstrip("/") + "/speed"
    try:
        if args.mode:
            resp = requests.post(url, json={"mode": args.mode}, timeout=8)
        else:
            resp = requests.get(url, timeout=8)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 2

    try:
        payload = resp.json()
    except Exception:
        payload = {"status_code": resp.status_code, "text": resp.text}

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if resp.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

