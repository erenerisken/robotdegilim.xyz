
class app_constants:
    # s3
    s3_bucket_name = "cdn.robotdegilim.xyz"
    aws_access_key_id = os.environ.get("ACCESS_KEY")
    aws_secret_access_key = os.environ.get("SECRET_ACCESS_KEY")
    # aws_region_name = os.environ.get('AWS_REGION')

    # Adaptive backoff factors (faster on good network, harsher on failures)
    adaptive_fast_base_delay = float(os.environ.get("ADAPTIVE_FAST_BASE_DELAY", "1.25"))
    adaptive_base_delay = float(os.environ.get("ADAPTIVE_BASE_DELAY", "1.5"))  # Base delay in seconds
    adaptive_slow_base_delay = float(os.environ.get("ADAPTIVE_SLOW_BASE_DELAY", "1.75"))
    adaptive_jitter = float(os.environ.get("ADAPTIVE_JITTER", "0.25"))
    adaptive_min_factor = float(os.environ.get("ADAPTIVE_MIN_FACTOR", "1.0"))
    adaptive_max_factor = float(os.environ.get("ADAPTIVE_MAX_FACTOR", "8.0"))
    adaptive_grow = float(os.environ.get("ADAPTIVE_GROW", "1.5"))
    adaptive_decay = float(os.environ.get("ADAPTIVE_DECAY", "1.1"))
    adaptive_successes_for_decay = int(os.environ.get("ADAPTIVE_SUCCESSES_FOR_DECAY", "10"))

    # Circuit breaker thresholds (open on sustained errors, cool down longer)
    breaker_fail_threshold = int(os.environ.get("BREAKER_FAIL_THRESHOLD", "10"))
    breaker_window_size = int(os.environ.get("BREAKER_WINDOW_SIZE", "50"))
    breaker_error_rate_threshold = float(os.environ.get("BREAKER_ERROR_RATE_THRESHOLD", "0.5"))
    breaker_cooldown_seconds = int(os.environ.get("BREAKER_COOLDOWN_SECONDS", "120"))
    breaker_probe_interval_seconds = int(os.environ.get("BREAKER_PROBE_INTERVAL_SECONDS", "30"))