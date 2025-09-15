# Environment Variable Reference

Central configuration variables read by `src/config.py`. Copy `.env.example` to `.env` for local development and override only what you need. All variables are read once at import (process start). Changing them at runtime requires a restart.

| Variable | Default | Type | Purpose | Notes |
|----------|---------|------|---------|-------|
| ACCESS_KEY | (none) | string | AWS access key for S3 uploads | Required in production |
| SECRET_ACCESS_KEY | (none) | string | AWS secret key | Required in production |
| MAIL_USERNAME | (none) | string | SMTP username for error emails | Optional |
| MAIL_PASSWORD | (none) | string | SMTP password | Optional |
| MAIL_RECIPIENT | info.robotdegilim@gmail.com | string | Destination for error notifications | Can override |
| ALLOWED_ORIGINS | * | string | CORS allow list (comma separated or `*`) | Parsed at startup |
| LOG_LEVEL | INFO | string | Minimum log level | One of DEBUG/INFO/WARN/ERROR |
| LOG_JSON | false | bool-ish | Enable JSON structured logging | Accepts 1/true/yes |
| APP_VERSION | 0.1.0 | string | Reported via `/status` | Bump per deploy |
| HTTP_TIMEOUT | 15.0 | float (s) | Per-attempt HTTP timeout | Applies to upstream fetches |
| GLOBAL_RETRIES | 10 | int | Max attempts per HTTP call | Inclusive of first attempt |
| THROTTLE_SCALE | 0.5 | float | Base multiplier for delays | Global tuning knob |
| THROTTLE_JITTER | 0.25 | float | Random jitter factor | 0 → no jitter |
| FAST_THROTTLE_SCALE | 0.1 | float | Preset fast mode scale | Used when recovering |
| SLOW_THROTTLE_SCALE | 1.0 | float | Preset slow mode scale | Used when degraded |
| ADAPTIVE_MIN_FACTOR | 1.0 | float | Lower bound for adaptive factor | Safeguard |
| ADAPTIVE_MAX_FACTOR | 8.0 | float | Upper bound for adaptive factor | Prevent runaway |
| ADAPTIVE_GROW | 1.5 | float | Multiplicative increase on failure cluster | Exponential-ish |
| ADAPTIVE_DECAY | 1.1 | float | Decay divisor applied after success streak | Works with successes count |
| ADAPTIVE_SUCCESSES_FOR_DECAY | 10 | int | Successes needed before applying decay | Controls stability |
| BREAKER_FAIL_THRESHOLD | 10 | int | Failures within window to consider open | See window size |
| BREAKER_WINDOW_SIZE | 50 | int | Sliding window size for error stats | Larger = smoother |
| BREAKER_ERROR_RATE_THRESHOLD | 0.5 | float (0-1) | Error ratio to open breaker | 0.5 = 50% |
| BREAKER_COOLDOWN_SECONDS | 120 | int | Time breaker stays fully open | No requests except probes |
| BREAKER_PROBE_INTERVAL_SECONDS | 30 | int | Interval between probe attempts | Probes test recovery |

## Resolution Order
1. Process environment
2. (Optionally) `.env` file if loaded by `python-dotenv` early (development convenience)
3. Hardcoded defaults inside `config.py`

## Adding a New Variable
1. Define in `config.py` with sensible default (string form from `os.environ.get`).
2. Document in `.env.example` with comment.
3. Add a row to this file and the backend README table.
4. If security-sensitive, keep value out of examples (use placeholder).

## Operational Guidance
- Keep `GLOBAL_RETRIES` moderate (10) to avoid prolonged runs under persistent failure.
- Increase `THROTTLE_SCALE` (e.g., to 0.8–1.2) if receiving polite rate signals or frequent 429.
- Decrease `ADAPTIVE_MAX_FACTOR` if backoff grows too aggressively.
- Breaker thresholds should reflect acceptable transient error ratio; 0.5 over a window of 50 offers balance.

## Security Considerations
- Never commit filled secrets into version control (`.env` is gitignored).
- Rotate AWS keys periodically; consider migrating to IAM roles if platform allows.
- Email credentials (if using Gmail) may require an app password (already the pattern in examples).

## Example Minimal Production Set
```
ACCESS_KEY=AKIA...
SECRET_ACCESS_KEY=...secret...
LOG_LEVEL=INFO
LOG_JSON=1
```

## Example Extended Tuning
```
GLOBAL_RETRIES=8
THROTTLE_SCALE=0.6
ADAPTIVE_MAX_FACTOR=6.0
BREAKER_ERROR_RATE_THRESHOLD=0.4
```

---
Generated and maintained alongside backend `README.md`. Keep them in sync.
