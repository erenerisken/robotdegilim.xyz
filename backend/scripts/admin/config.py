"""Static configuration for admin helper scripts."""

from pathlib import Path

# Edit these values directly for your environment/workflow.
BASE_URL = "http://127.0.0.1:8000"
ADMIN_SECRET = ""
TIMEOUT_SECONDS = 15
VERIFY_TLS = True

# ./.admin_lock_token
TOKEN_FILE_PATH = Path(__file__).resolve().parent.parent / ".admin_lock_token"