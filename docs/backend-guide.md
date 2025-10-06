# Backend Guide

## Overview
The backend is a synchronous Flask application that exposes operational endpoints, manages scrape/must/NTE jobs, and publishes JSON artifacts to S3. This guide complements `backend/README.md` by summarizing key modules, API contracts, and operational tooling.

## Runtime Requirements
- Python 3.12 (recommended)
- Dependencies listed in `backend/requirements.txt`
- Optional development dependencies (`backend/requirements-dev.txt`) for linting, typing, and testing
- AWS credentials with write access to the target S3 bucket (`cdn.robotdegilim.xyz`)

## Package Structure
```
backend/
├── src/
│   ├── app.py                # Flask routes and job orchestration
│   ├── config.py             # Environment-backed constants and paths
│   ├── errors.py             # Structured error hierarchy (AppError, BusyError, etc.)
│   ├── services/status_service.py
│   ├── scrape/               # HTML fetch + parse pipeline
│   ├── musts/                # Mandatory course generation
│   ├── nte/                  # NTE list + availability generation
│   └── utils/                # HTTP, publish, logging, timing utilities
├── storage/                  # Local cache for generated JSON + logs
├── scripts/                  # Operational scripts (deploy packaging, throttling)
└── tests/                    # Pytest suite covering endpoints + pipelines
```

## API Surface
| Method | Path | Description | Success | Busy/Deferred |
|--------|------|-------------|---------|---------------|
| GET | `/` | Root with service metadata and available routes | `200` JSON | — |
| GET | `/run-scrape` | Executes full scrape (fetch → parse → publish) and NTE generation. If musts are queued they run afterwards. | `200` `{ "status": "Scraping and NTE completed successfully" }` | `503` `{ "code": "BUSY" }` |
| GET | `/run-musts` | Generates must course dataset. If scrape incomplete, queues run. | `200` `{ "code": "OK" }` | `202` `{ "code": "QUEUED" }` |
| GET | `/status` | Current status, version, throttle mode, queue info. | `200` JSON | — |
| GET | `/speed` | Returns current throttle mode (`fast`, `normal`, `slow`) and adaptive metrics. | `200` JSON | — |
| POST | `/speed` | Updates throttle mode. Body: `{ "mode": "fast" | "slow" | "normal" }`. | `200` JSON | — |

All error responses are emitted via `AppError` subclasses with JSON payloads containing `code`, `message`, and optional `details` metadata.

## Job Lifecycles
1. **Scrape**
   - Ensures no other run is active via `status_service`.
   - Fetches department/course data with adaptive throttling (base scale configurable via `/speed`).
   - Writes JSON artifacts to `storage/data/`.
   - Publishes artifacts to S3 using `src/utils/publish.commit_snapshot`, uploading `lastUpdated.json` last.
2. **Musts**
   - Requires latest `data.json`.
   - Generates must course list and persists to `musts.json`.
   - Uploads output alongside scrape artifacts when invoked post-scrape or via `/run-musts`.
3. **NTE**
   - Reads `nteList.json`, `departments.json`, `data.json`.
   - Validates non-empty result and writes `nteAvailable.json`.
   - Publishes output as part of the scrape pipeline.

## Local Storage Contracts
- `storage/data/` – Working directory for generated JSON prior to publish (not bundled into deployment images).
- `storage/logs/` – Rotating log files (`app.log`, `jobs.log`, `error.log`).

## Configuration Highlights
- `ACCESS_KEY`, `SECRET_ACCESS_KEY` – Mandatory for S3 publish.
- `LOG_LEVEL`, `LOG_JSON` – Logging behavior.
- `HTTP_TIMEOUT`, `GLOBAL_RETRIES`, `THROTTLE_*` – HTTP client tuning.
- `BREAKER_*` – Circuit breaker thresholds controlling upstream request pacing.
- `MAIL_*` – Optional SMTP settings for alerting utilities.

## Testing & Tooling
- Run unit/integration tests: `python -m pytest backend/tests`.
- Lint/format/type-check: `ruff check src`, `black src`, `mypy src`.
- `backend/Makefile` provides convenience targets (`make test`, `make lint`, etc.).

## Deployment Workflow
1. Generate Fly.io package: `python backend/scripts/make_fly_deploy.py --force`.
2. Review generated `fly-io/robotdegilim/` folder (Dockerfile, fly.toml, requirements.txt, src/ snapshot).
3. Configure Fly secrets: `fly secrets set ACCESS_KEY=... SECRET_ACCESS_KEY=... MAIL_USERNAME=... MAIL_PASSWORD=...`.
4. Deploy: `fly deploy` from the generated folder.
5. Monitor `/status` and Fly health checks.

## Observability
- Structured logging with `AppError` metadata for actionable error messages.
- `/status` includes adaptive throttle factor, queued jobs, last successful runs.
- `speed.py` script provides CLI access to `/speed` for operators.

## Extensibility Guidelines
- Add new environment variables to `config.py`, `.env.example`, and update documentation.
- Centralize HTTP access through `src/utils/http` to inherit throttle and breaker behavior.
- Maintain idempotency in publish helpers to ensure safe restarts.
- Update/extend pytest suite when altering pipelines or API contracts.
