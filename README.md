<div align="center">

# Robot Değilim

Scrape → Normalize → Publish → Visualize. A Python (Flask) backend turns METU OIBS course data into atomic JSON snapshots on S3; a React frontend renders schedules & course views from those published artifacts.

</div>

## Monorepo Layout
| Path | Description |
|------|-------------|
| `backend/` | Flask scraping + publish service (detailed docs in `backend/README.md` and `docs/backend-guide.md`) |
| `frontend/` | React UI consuming public JSON + control endpoints (see `docs/frontend-guide.md`) |
| `docs/` | Project-wide documentation (architecture, data contracts, deployment) |

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
- Deploy image includes only code + dependencies; runtime JSON is generated on demand and uploaded to S3.
- Frontend can be shipped as a static site (Netlify, S3+CloudFront, etc.) consuming the published JSON.

## Documentation Index
- `docs/architecture.md` – end-to-end data flow, key components, and resilience design.
- `docs/backend-guide.md` – API endpoints, job lifecycles, storage contracts, and operations.
- `docs/frontend-guide.md` – React app structure, state flow, and integration with backend artifacts.
- `backend/README.md` – in-depth backend developer guide.
- `frontend/README.md` – frontend workflow, scripts, and customizations.

## Contributing
1. Create a feature branch.
2. Update docs if env vars or endpoints change.
3. Run backend + frontend linters/tests.
4. Open PR.

## License
MIT – see `LICENSE`.