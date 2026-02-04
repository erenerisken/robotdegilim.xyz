# robotdegilim backend

FastAPI backend for `robotdegilim.xyz`.

This service runs data pipelines (`scrape`, `musts`, `nte list`, `nte available`), stores shared state in S3 (or local mock), and exposes run/admin endpoints.

## Tech stack

- Python 3.12+
- FastAPI + Uvicorn
- Pydantic v2 / pydantic-settings
- Requests + BeautifulSoup
- boto3 (real S3 mode)

## Project layout

```text
backend/
  app/
    api/         # routes + schemas
    context/     # app context schema/service
    core/        # settings, constants, logging, errors, paths
    pipelines/   # orchestrators
    scrape/      # scrape-specific fetch/parse/io
    musts/       # musts-specific fetch/parse/io
    nte/         # nte-specific fetch/parse/io
    services/    # request/admin/settings services
    storage/     # local + s3 storage adapters
    utils/       # cache/http utils
    main.py      # FastAPI app entrypoint
  scripts/
    make_fly_deploy.py
    admin/
  data/          # local runtime files
  s3-mock/       # local mock S3 files
  tests/         # unittest suite
```

## Setup

From `backend/`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy env template:

```powershell
Copy-Item .env.example .env
```

Fill required values in `.env`:

- `ADMIN_SECRET`
- `S3_BUCKET` (+ `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`) for real S3 mode

If `S3_BUCKET` is empty, storage falls back to local `s3-mock/`.

## Run locally

From `backend/`:

```powershell
uvicorn app.main:app --reload
```

Default API base: `http://127.0.0.1:8000`

## Endpoints

- `GET /` - root metadata
- `GET /run-scrape` - trigger scrape pipeline
- `GET /run-musts` - trigger musts pipeline
- `POST /admin` - admin actions

Admin auth headers:

- `X-Admin-Secret` (required)
- `X-Admin-Lock-Token` (required for mutating admin actions)

Supported admin actions:

- `admin_lock_acquire`
- `admin_lock_release`
- `admin_lock_status`
- `context_get`
- `context_clear_queue`
- `context_reset_failures`
- `context_unsuspend`
- `settings_get`
- `settings_set`

## Admin helper scripts

Script package: `scripts/admin/`

Important files:

- `scripts/admin/config.py` - set `BASE_URL`, `ADMIN_SECRET`, timeout, token path
- `scripts/admin/main.py` - scenario runner (edit which flow to call)

Run:

```powershell
python scripts/admin/main.py
```

Token behavior:

- Lock acquire stores token in `backend/.admin_lock_token`
- Mutating admin actions use this token
- Lock release removes token file

## Deploy folder builder (Fly.io)

Build deploy-ready folder:

```powershell
python scripts/make_fly_deploy.py
```

Optional:

```powershell
python scripts/make_fly_deploy.py --out .deploy/fly --app-name robotdegilim-backend
```

The script copies required sources, keeps `data/raw`, creates empty runtime dirs, and generates:

- `Dockerfile`
- `fly.toml`
- `.dockerignore`

## Tests

From `backend/`:

```powershell
python -m unittest discover -s tests
```

## Data and runtime notes

- `data/` and `s3-mock/` are runtime folders.
- Folder structure is versioned with `.gitkeep`; runtime files are git-ignored.
- Logs are written under `data/logs/`.

## Security notes

- Never commit `.env` or `.admin_lock_token`.
- Keep `ADMIN_SECRET`, mail credentials, and S3 credentials private.
