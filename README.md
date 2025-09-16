<div align="center">

# Robot Değilim

Scrape → Normalize → Publish → Visualize. A Python (Flask) backend turns METU OIBS course data into atomic JSON snapshots on S3; a React frontend renders schedules & course views from those published artifacts.

</div>

## Monorepo Layout
| Path | Description |
|------|-------------|
| `backend/` | Flask scraping + publish service (see its README for deep details) |
| `frontend/` | React UI (Create React App) consuming public JSON + control endpoints |

## High-Level Flow
1. Backend scrapes source HTML with adaptive throttling.
2. Builds complete dataset locally, then uploads JSON files to S3.
3. Commits new snapshot by uploading `lastUpdated.json` last (atomic publish signal).
4. Frontend fetches JSON (and optional status endpoint) to render UI.

## Quick Start
### Backend (Dev)
```
python -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1   # Windows PowerShell
python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
cp backend/.env.example backend/.env  # add AWS + optional email creds
python -m flask --app backend/src/app run -p 3000
```

### Frontend (Dev)
```
cd frontend
npm ci
npm start
```
Visit http://localhost:3000 (backend) and the CRA dev server (default http://localhost:3001 or 3000 depending on your setup).

## Environment
Primary variables live in `backend/.env.example`. Key ones: `ACCESS_KEY`, `SECRET_ACCESS_KEY`, optional mail creds, and tuning knobs (timeouts, retries, breaker thresholds). See `backend/README.md` for the full table. A `pyproject.toml` is not required for deployment; the image installs from `requirements.txt`.

## Scripts & Tooling
- Lint/type (backend): `ruff`, `black`, `mypy`
- Frontend tests: `npm test`
- Frontend build: `npm run build`

## Deployment Overview
- Backend runs on Fly.io with Python 3.12 via Gunicorn (default: workers=2, timeout=0) and `/status` health checks, with env defaults including `ALLOWED_ORIGINS=*`.
- Only `backend/storage/data/manualPrefixes.json` is bundled into the deploy image when present.
- Outputs JSON to S3 (bucket name defined in backend config).
- Frontend can be a static site (Netlify, S3+CloudFront, etc.) consuming the published JSON.

## Contributing
1. Create a feature branch.
2. Update docs if env vars or endpoints change.
3. Run backend + frontend linters/tests.
4. Open PR.

## License
MIT – see `LICENSE`.