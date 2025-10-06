<div align="center">

# robotdegilim-backend

Lightweight Flask service that scrapes METU OIBS data, builds consistent JSON artifacts, and publishes them atomically to S3. Includes an adaptive throttling layer, retries, and a circuit breaker to remain polite to upstream systems.

</div>

## Table of Contents
1. Why it exists
2. High-level architecture
3. Data flow / publish model
4. Endpoints
5. Directory layout
6. Environment variables
7. Local development
8. Deployment
9. Operations & observability
10. Failure modes & resilience
11. Contributing / style
12. Troubleshooting FAQ

## 1. Why It Exists
Schools publish course & schedule data behind legacy HTML forms. This service turns that into stable, versioned JSON for a React frontend and other consumers, ensuring clients never observe half-written data.

## 2. High-Level Architecture
Single-process synchronous Flask app. A run consists of: fetch → parse → assemble in-memory structures → write local JSON → upload to S3 → upload `lastUpdated.json` last. State (busy/idle, queued operations) is persisted in `status.json` (both locally and on S3) to coordinate scrape vs must runs.

Key resilience pieces:
- Centralized HTTP wrapper with: per-attempt timeout, bounded global retries (`GLOBAL_RETRIES`), adaptive delay scaling, jitter, and classification of retryable vs fatal errors.
- Circuit breaker (rolling window) to stop hammering upstream when error rate exceeds threshold.
- Atomic publish: only after every data file succeeds do we flip the pointer (`lastUpdated.json`).

## 3. Data Flow / Publish Model
1. Build everything locally under `storage/data/`.
2. Upload content files (`departments*.json`, `data.json`, `musts.json`, etc.).
3. Only after success upload `lastUpdated.json` (acts like a “commit”).
4. Frontend polls or fetches using public S3 URLs; seeing a new `lastUpdated.json` timestamp means a coherent dataset is available.

If a failure occurs mid-upload: restart is safe; clients keep prior snapshot.

## 4. Endpoints
| Method | Path         | Description | Success Response | Busy/Deferred |
|--------|--------------|-------------|------------------|---------------|
| GET    | /            | Root; service info and listed endpoints | 200 JSON | — |
| GET    | /run-scrape  | Run full scrape, then NTE; run queued musts if any | 200 `{status:"Scraping and NTE completed successfully"}` | 503 `{code:"BUSY"}` |
| GET    | /run-musts   | Generate musts if data ready else queue | 200 `{code:"OK"}` | 202 `{code:"QUEUED"}` |
| GET    | /status      | Current status + version + flags | 200 JSON | — |
| GET/POST | /speed     | Get or set throttling mode: fast | slow | normal | 200 `{mode, scale, ...}` | — |

Notes on /speed:
- GET returns current mode, effective scale, adaptive factor, and breaker state.
- POST requires a JSON body: `{ "mode": "fast" | "slow" | "normal" }`.

## 5. Directory Layout
```
src/
  app.py                # Flask app / routes
  config.py             # Environment + constants
  errors.py             # Structured error types
  services/status_service.py
  scrape/               # Scrape orchestration + fetch/parse/io
  musts/                # Musts orchestration + helpers
  nte/                  # NTE processing (reads data.json, departments.json, nteList.json; writes nteAvailable.json)
  utils/                # http, timing, s3, publish, logging, run helpers
storage/
  data/                 # Generated JSON artifacts (local) 
  logs/                 # Runtime logs
scripts/                # Maintenance / perf scripts
```

## 6. Environment Variables
Primary variables (see also `../.env.example`):

| Name | Default | Purpose | Notes |
|------|---------|---------|-------|
| ACCESS_KEY | — | AWS access key for S3 | Required in prod |
| SECRET_ACCESS_KEY | — | AWS secret key for S3 | Required in prod |
| MAIL_USERNAME | — | SMTP auth user | Optional, enables email alerts |
| MAIL_PASSWORD | — | SMTP auth password | Optional |
| MAIL_RECIPIENT | info.robotdegilim@gmail.com | Alert destination | Can override |
| ALLOWED_ORIGINS | * | CORS origins | Comma list or * |
| LOG_LEVEL | INFO | Logging level | Uppercase |
| LOG_JSON | false | JSON vs plain logs | 1/true/yes accepted |
| APP_VERSION | 0.1.0 | Reported via /status | Override at deploy |
| HTTP_TIMEOUT | 15.0 | Per attempt timeout (s) | Float seconds |
| GLOBAL_RETRIES | 10 | Total retry attempts per request | Applies across wrappers |
| THROTTLE_SCALE | 0.5 | Base multiplier for delays | Increase to slow globally |
| THROTTLE_JITTER | 0.25 | Random fractional jitter | 0 disables |
| FAST_THROTTLE_SCALE | 0.1 | "Fast mode" scale | For low-lat runs |
| SLOW_THROTTLE_SCALE | 1.0 | "Slow mode" scale | Recovery / politeness |
| ADAPTIVE_MIN_FACTOR | 1.0 | Min adaptive factor | Lower bound |
| ADAPTIVE_MAX_FACTOR | 8.0 | Max adaptive factor | Upper bound |
| ADAPTIVE_GROW | 1.5 | Growth multiplier on failures | Exponential-ish |
| ADAPTIVE_DECAY | 1.1 | Decay factor on success streak | Shrinks factor |
| ADAPTIVE_SUCCESSES_FOR_DECAY | 10 | Successes to apply decay | Integer |
| BREAKER_FAIL_THRESHOLD | 10 | Fail count to trip breaker | Within window |
| BREAKER_WINDOW_SIZE | 50 | Sample window size | Rolling |
| BREAKER_ERROR_RATE_THRESHOLD | 0.5 | Error ratio to open breaker | 0-1 |
| BREAKER_COOLDOWN_SECONDS | 120 | Time breaker stays open | Seconds |
| BREAKER_PROBE_INTERVAL_SECONDS | 30 | Probe interval while open | Seconds |

Tip (Windows PowerShell): copy the example env file with:
```
Copy-Item .env.example .env
```

## 7. Local Development
Create a venv and install runtime + optional dev deps:
```
# Create and activate venv (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install deps
python -m pip install -r requirements.txt -r requirements-dev.txt

# Create local env file
Copy-Item .env.example .env  # then fill required secrets

# Run dev server
python -m flask --app src/app run -p 3000
```

Optional (if you have Make):
```
make dev-install
make run PORT=3000
```

Speed controls during dev (throttling):
- Using helper script:
```
python .\scripts\speed.py --base-url http://localhost:3000         # show
python .\scripts\speed.py fast --base-url http://localhost:3000    # set fast
python .\scripts\speed.py slow --base-url http://localhost:3000    # set slow
python .\scripts\speed.py normal --base-url http://localhost:3000  # set normal
```
- Direct API calls (PowerShell):
```
Invoke-RestMethod -Uri http://localhost:3000/speed -Method Get
Invoke-RestMethod -Uri http://localhost:3000/speed -Method Post -ContentType 'application/json' -Body '{"mode":"fast"}'
```

Useful commands:
```
ruff check src
black src
mypy src
```

## 8. Deployment
- Provide environment via platform secret store (e.g. `flyctl secrets set ACCESS_KEY=...`).
- Install only production requirements if you want lean images.
- Run under a WSGI server:
```
# From project root or backend/, either of these forms:
gunicorn 'app:app' -b 0.0.0.0:3000 --chdir ./src --workers 1 --threads 4 --timeout 180
# or explicitly reference the module path:
gunicorn 'src.app:app' -b 0.0.0.0:3000 --workers 1 --threads 4 --timeout 180
```

### 8.0 Environment on Fly
- Non-secret runtime defaults are written to `fly.toml [env]` by the generator:
  - `LOG_LEVEL=INFO`, `LOG_JSON=false`, `APP_VERSION=0.1.0`, `ALLOWED_ORIGINS=*`
- Secrets must be set via Fly:
  - `fly secrets set ACCESS_KEY=... SECRET_ACCESS_KEY=... MAIL_USERNAME=... MAIL_PASSWORD=...`
- Health check: The generator adds an HTTP check on `/status` (10s interval, 2s timeout).

### 8.1 Generate Fly.io deploy folder
Use the helper script to assemble a clean deployable directory (Dockerfile, fly.toml, requirements.txt, src/):

- From repo root, PowerShell:
  - `python backend/scripts/make_fly_deploy.py --force`

Defaults:
- Output: `fly-io/robotdegilim`
- App name: `robotdegilim-xyz` (override with `--app-name <name>`)
- Region: `otp` (override with `--region <code>`)
- Python: `3.12` (override with `--python-version <x.y.z>`)

Then deploy from the generated folder:
- `fly auth login` (if needed)
- `fly apps create <app-name>` (first time)
- `fly secrets set ACCESS_KEY=... SECRET_ACCESS_KEY=... MAIL_USERNAME=... MAIL_PASSWORD=...`
- `fly deploy`

Using previous templates:
- If you have a prior deploy folder (e.g., `C:\Users\3alka\Masaustu\Projects\fly-io\robotdegilim`), you can import its Dockerfile and fly.toml and patch them:
  - `python backend/scripts/make_fly_deploy.py --force --from-templates "C:\\Users\\3alka\\Masaustu\\Projects\\fly-io\\robotdegilim"`
  - You may still override `--app-name`, `--region`, or `--python-version`.

Runtime config baked into Dockerfile:
- Gunicorn workers: `--gunicorn-workers N` (default 2). A worker is a process handling requests; 2 keeps /status responsive while one worker runs a long job.
- Gunicorn timeout: `--gunicorn-timeout S` (default 0 for no timeout). 0 avoids killing long-running scrape/musts; set a large finite value if you prefer a safety net.

NTE artifacts:
- Input expected (from S3 or local cache): `data.json`, `departments.json`, `nteList.json`.
- Output produced after successful scrape: `nteAvailable.json` (uploaded to S3 and written under `storage/data/`).

Data files included:
- Deploy bundles only the application code and requirements. Generated JSON artifacts stay out of the image; they are produced locally at runtime and uploaded to S3.

Notes:
- A `pyproject.toml` is not required for deployment since we install with `requirements.txt`. Keep `pyproject.toml` only if you move to PDM/Poetry or need build-system metadata.

### 8.2 Fly deployment checklist
1. `fly auth login`
2. `fly apps create <app-name>` (first time)
3. Set secrets: `fly secrets set ACCESS_KEY=... SECRET_ACCESS_KEY=... [MAIL_USERNAME=... MAIL_PASSWORD=...]`
4. `fly deploy`
5. Verify `/status` on the deployed app and check Fly health checks.

## 9. Operations & Observability
Artifacts:
- S3 bucket (configured in `config.app_constants.s3_bucket_name`) stores JSON.
- `status.json` communicates system state to operators and frontend.
 - `nteAvailable.json` contains currently available NTE courses (built post-scrape).

Logging:
- Plain text (default) or structured JSON with `LOG_JSON=1`.
- Daily rotation (TR timezone) performed by logging configuration.

## 10. Failure Modes & Resilience
| Scenario | Mitigation |
|----------|------------|
| Upstream latency spike | Adaptive factor grows; delays increase |
| Burst of 5xx/429 | Retries with backoff; may trip breaker |
| Sustained errors | Breaker opens; periodic probes to resume |
| Partial upload failure | `lastUpdated.json` not replaced → previous snapshot remains |
| Musts requested early | Queued until first successful scrape completes |
| Speed switch invalid body | 400 with validation error | Ensure JSON body with mode is provided |

## 11. Contributing / Style
- Keep synchronous model (avoid premature async/concurrency).
- Add new env vars to: `config.py`, `.env.example`, and this README table.
- Run ruff/black/mypy before PRs.

## 12. Troubleshooting FAQ
| Symptom | Explanation | Action |
|---------|-------------|--------|
| 503 BUSY on /run-scrape | A run is already active | Retry later / check /status |
| 202 QUEUED from /run-musts | Data not ready | Run scrape first or wait |
| Slow progress | Adaptive backoff elevated | Inspect logs for failures |
| No new data published | Upload failed before final commit | Check error logs |
| 400 from POST /speed | Missing or invalid JSON body | Send `{ "mode": "fast|slow|normal" }` |
| NTE output missing | No available sections matched or missing inputs | Verify `nteList.json`, `departments.json`, and `data.json` are present |

## License
MIT (see root `LICENSE`).

