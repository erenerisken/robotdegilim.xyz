# robotdegilim-backend

Backend service that scrapes METU OIBS data, produces JSON artifacts, and publishes them to S3. It exposes admin endpoints to trigger scrape and “musts” generation, with built‑in backoff/circuit‑breaker for politeness and an end‑only, atomic publish model.

## Overview
- Single-process Flask app; no concurrency by design.
- Scraper builds data in memory, writes to `storage/data/`, uploads to S3, then uploads `lastUpdated.json` last (publish signal) so clients never see partial data.
- Robust HTTP layer with timeouts, retries, adaptive backoff, and a circuit breaker.
- State in S3 (`status.json`): `status`, `queued_musts`, `depts_ready`. Initialized on startup.

## Endpoints
- `GET /run-scrape`
  - 200 OK `{ status: "Scraping completed successfully" }`
  - 503 BUSY `{ status: "System is busy", code: "BUSY" }`
  - If `queued_musts` was set, runs musts right after a successful scrape.
- `GET /run-musts`
  - 200 OK `{ status: "Get musts completed successfully", code: "OK" }`
  - 202 QUEUED when data not ready or scraper is busy.
- `GET /status`
  - `{"status":"idle|busy","queued_musts":bool,"depts_ready":bool,"version":string}`

## Layout
- `src/app.py` – Flask entrypoint (CORS, access log, security headers, JSON logs, routes)
- `src/config.py` – Central config (env, file names, dirs, headers)
- Scraper:
  - `src/scrape/scrape.py` – Orchestrates the scrape run
  - `src/scrape/fetch.py` – All METU HTTP calls (via wrappers)
  - `src/scrape/parse.py` – HTML parsing → structured data
  - `src/scrape/io.py` – JSON read/write, prefix loaders
- Musts:
  - `src/musts/musts.py` – Orchestrates musts run
  - `src/musts/fetch.py`, `src/musts/parse.py`, `src/musts/io.py`
- Services/Utils:
  - `src/services/status_service.py` – read/write status.json; set busy/idle
  - `src/utils/http.py` – requests.Session factory and robust request wrappers
  - `src/utils/timing.py` – adaptive backoff + circuit breaker
  - `src/utils/s3.py` – S3 client, uploads with retries, idle check
  - `src/utils/publish.py` – uploads files, then `lastUpdated.json`
  - `src/utils/run.py` – `busy_idle` context manager
  - `src/utils/logging.py` – JSON log formatter
  - `src/errors.py` – `AppError` and `RecoverError` (structured, redacted)

## Storage
- Local (created on demand):
  - Logs: `backend/storage/logs/`
  - Data: `backend/storage/data/`
- S3 keys (see `config.py`):
  - `departments.json`, `departmentsNoPrefix.json`, `manualPrefixes.json` (optional), `data.json`, `musts.json`, `lastUpdated.json`, `status.json`

## Configuration
- Dev: set env in `backend/.env` (gitignored). The app loads it early using `python-dotenv` if installed.
- Prod (Fly.io): set secrets as environment variables via `flyctl secrets set`.
- Env vars (subset):
  - `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_RECIPIENT` – error email (optional)
  - `ACCESS_KEY`, `SECRET_ACCESS_KEY` – S3 ( Fly.io has no IAM roles )
  - `ALLOWED_ORIGINS` – CORS (comma-separated or `*`)
  - `LOG_JSON` – `1/true/yes` for JSON logs; otherwise text logs
  - `APP_VERSION` – exposed via `/status`

## Running
- Dev (Windows example):
  - `pip install -r backend/requirements.txt -r backend/requirements-dev.txt`
  - `set FLASK_ENV=development` (optional)
  - `python -m flask --app backend/src/app run -p 3000`
- Prod (Fly):
  - Install only `backend/requirements.txt`
  - Use `gunicorn 'app:app' -b 0.0.0.0:3000` or equivalent.

## Scraping Behavior (politeness)
- Every request goes through `throttle_before_request()` with adaptive backoff + jitter.
- Circuit breaker opens on many failures/high error rate, cools down briefly, probes to resume.
- `utils/http.request()` wraps request attempts and classifies failures (429/5xx retried; hard 4xx aborts).
- No concurrency; single-process runs. Add a global run timeout later if desired.

## Publish Model
- Build everything in memory; write to `storage/data/`.
- Upload data files with retries; then upload `lastUpdated.json` last (publish signal).
- If any upload fails, lastUpdated does not change → clients keep previous complete dataset.

## Error Handling & Logging
- `RecoverError(message, details, code)` aborts runs cleanly without partial state.
- Text logs: rotated daily (TR timezone). Access log includes request_id.
- JSON logs: set `LOG_JSON=1` to structure logs with timestamps, levels, logger, and message.

## Development
- Lint/format/type check (optional):
  - `ruff check backend/src`
  - `black backend/src`
  - `mypy backend/src`

## Troubleshooting
- “System is busy”: status.json is not `idle`; wait or check `/status`.
- “Queued to run after scrape”: musts requested before departments data is ready; it will run after the next successful scrape.
- Frequent 429/5xx: scraper will slow down via adaptive backoff/breaker. Consider trying later.

## Notes & Small Gotchas
- `manualPrefixes.json` is optional. The publisher skips uploading it if the local file is missing.
