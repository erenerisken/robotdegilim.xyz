# Architecture Overview

## Purpose and Scope
This document describes how the Robot Değilim platform converts raw university schedule data into consumable JSON and renders it for end users. It captures runtime data flow, infrastructure roles, and resilience features that apply to both the backend scraping service and the frontend visualization layer.

## System Landscape
- **Backend (`backend/`)** – A Flask application that exposes operational endpoints, coordinates scrape/must/NTE jobs, persists artifacts locally under `backend/storage`, and publishes new snapshots to S3.
- **Artifact Storage (S3)** – Holds all published JSON outputs (`data.json`, `departments.json`, `musts.json`, `nteAvailable.json`, `lastUpdated.json`, etc.). Acts as the single source of truth for consumers.
- **Frontend (`frontend/`)** – A React single-page application that loads published JSON artifacts and displays schedule, musts, and NTE data with interactive controls.
- **Operators / Tooling** – CLI scripts under `backend/scripts` (e.g., `make_fly_deploy.py`, `speed.py`) and Fly.io deployment assets under `fly-io/robotdegilim`.

## End-to-End Data Flow
1. **Trigger** – A GET request to `/run-scrape` (or scheduled job) initiates a full scrape.
2. **Fetch** – Backend modules under `src/scrape` perform HTTP requests to upstream sources using adaptive throttling with retries and jitter.
3. **Parse** – HTML responses are parsed into structured Python objects (`src/scrape/parse.py`).
4. **Assemble** – Data is consolidated into coherent models (`src/musts`, `src/nte`, `src/utils/run`).
5. **Persist Locally** – Intermediate and final JSON files are written under `backend/storage/data/`.
6. **Publish** – Files are uploaded to S3 via `src/utils/publish.py`, ensuring `lastUpdated.json` is uploaded last so consumers only see fully consistent snapshots.
7. **Expose** – Frontend fetches JSON artifacts from S3 (or optionally proxied through the backend) and renders them. Operational endpoints like `/status` and `/speed` support observability and throttling controls.

## Key Concepts
- **Atomic Publishing** – `lastUpdated.json` acts as a commit marker; if publishing fails before this file, clients continue to read the previous snapshot.
- **Adaptive Throttling & Circuit Breaker** – Implemented in `src/utils/http.py` and related utilities to respect upstream limits.
- **Status Tracking** – `src/services/status_service.py` maintains `status.json` detailing the current run state, queue status for musts, and version metadata.
- **Musts vs NTE Pipelines** – Distinct modules generate mandatory course lists (musts) and non-technical elective availability (NTE). Both depend on the canonical `data.json` dataset.

## Runtime Topology
- **Development** – Flask runs locally (default port 3000). React dev server runs via CRA (default port 3000/3001). Local storage persists under `backend/storage`.
- **Production** – Backend containerized via Fly.io. Gunicorn serves the Flask app with configurable worker count and timeout. Frontend deployed as static assets (hosting platform agnostic) referencing S3 endpoints.

## Secrets and Configuration
- **Environment Variables** – Defined in `backend/.env.example`, loaded via `dotenv` for local development. Production secrets are set via Fly.io.
- **Configuration Module** – `backend/src/config.py` centralizes paths, bucket names, logging, throttling, and breaker settings.

## Observability & Operations
- **Logs** – Structured/pretty logs controlled by `LOG_JSON` and `LOG_LEVEL`. Log files rotate daily within `backend/storage/logs`.
- **Status Endpoint** – `/status` returns service version, run state, and throttle mode. Fly.io health checks poll this endpoint.
- **Speed Endpoint** – `/speed` reports and manipulates throttling modes (`fast`, `normal`, `slow`).
- **Error Handling** – `src/errors.py` defines structured `AppError` variants with metadata for consistent responses and logging.

## Failure Modes & Resilience
- **Network Flakiness** – Retries with exponential backoff and jitter; breaker temporarily halts requests if error-rate threshold exceeded.
- **Partial Publish** – Intermediate files stored locally; publish resumes safely without corrupting client-facing data.
- **Concurrent Runs** – Status service enforces single active run, queueing musts when a scrape is already in progress.

## File & Module Relationships
```
backend/src
├── app.py               # Flask routes, job orchestration
├── config.py            # Environment constants
├── errors.py            # Structured error types
├── services/
│   └── status_service.py
├── scrape/
│   ├── fetch.py         # HTTP wrappers
│   ├── parse.py         # HTML parsing
│   └── scrape.py        # End-to-end scrape orchestration
├── musts/
│   └── musts.py         # Must course generation
├── nte/
│   └── nte_available.py # NTE computation and validation
└── utils/
    ├── http.py          # Throttled HTTP client
    ├── publish.py       # S3 publication helpers
    ├── run.py           # Job lifecycle helpers
    └── logging.py       # Logging configuration
```
Frontend modules under `frontend/src` include `App.js` for routing/state, `Controls.js` and `WeeklyProgram.js` for key UI views, and `slices/` for Redux-like state management.

## Deployment Summary
- Use `python backend/scripts/make_fly_deploy.py --force` to generate a clean Fly.io folder under `fly-io/robotdegilim`.
- Deploy with `fly deploy` after ensuring secrets (`ACCESS_KEY`, `SECRET_ACCESS_KEY`, mail credentials) are set.
- Frontend builds with `npm run build` and can be deployed to any static host; ensure environment is configured to fetch JSON from the correct S3 bucket or backend proxy.

For deeper backend details see `docs/backend-guide.md`. For frontend structure and integration specifics see `docs/frontend-guide.md`.
