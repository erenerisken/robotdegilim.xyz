from __future__ import annotations

import sys
from pathlib import Path


_BACKEND_PATH = Path(__file__).resolve().parents[1]
_backend_str = str(_BACKEND_PATH)
if _backend_str not in sys.path:
    sys.path.insert(0, _backend_str)
