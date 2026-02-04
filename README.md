# robotdegilim.xyz

Monorepo for the `robotdegilim.xyz` project:

- `backend/`: FastAPI data pipelines + admin/run APIs
- `frontend/`: React schedule UI consuming public JSON artifacts

---

## Repository Structure

```text
robotdegilim.xyz/
  backend/
    app/           # API, pipelines, services, storage adapters
    scripts/       # fly deploy builder + admin helper scripts
    data/          # local runtime files
    s3-mock/       # local mock S3
    tests/         # backend unittest suite
  frontend/
    src/           # React app
    public/        # static assets
```

---

## Local Development

## 1) Backend

From `backend/`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Backend base URL: `http://127.0.0.1:8000`

Detailed backend docs: `backend/README.md`

## 2) Frontend

From `frontend/`:

```powershell
npm ci
npm start
```

Frontend base URL: `http://localhost:3000`

Detailed frontend docs: `frontend/README.md`

---

## Integration Overview

- Backend publishes public JSON files (S3 or `s3-mock` in local mode).
- Frontend reads these files via `frontend/src/Client.js`.
- Frontend checks `status.json` before triggering scrape.
  - `status: "idle"` -> scrape trigger allowed
  - otherwise -> scrape trigger skipped

---

## Deploy Helpers

From `backend/`:

- Build deploy-ready Fly folder:
  - `python scripts/make_fly_deploy.py`
- Admin helper scripts:
  - `python scripts/admin/main.py`

---

## Testing

From `backend/`:

```powershell
python -m unittest discover -s tests
```

From `frontend/`:

```powershell
npm test
```

---

## Security Notes

- Never commit real secrets from `.env`.
- Keep admin token file (`backend/.admin_lock_token`) private.
- Keep S3 and mail credentials in environment/secret manager.

