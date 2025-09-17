from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import time
from src.config import app_constants


_last_request_time: datetime | None = None


def _check_delay(delay: float = 1.0):
    """Ensure at least `delay` seconds between calls in this process.

    Useful to throttle scraping requests and be polite to remote servers.
    """
    global _last_request_time
    now = datetime.now()
    if _last_request_time and now - _last_request_time < timedelta(seconds=delay):
        time.sleep(delay - (now - _last_request_time).total_seconds())
        now = datetime.now()
    _last_request_time = now


@dataclass
class AdaptiveBackoff:
    min_factor: float = app_constants.adaptive_min_factor
    max_factor: float = app_constants.adaptive_max_factor
    grow: float = app_constants.adaptive_grow
    decay: float = app_constants.adaptive_decay
    successes_for_decay: int = app_constants.adaptive_successes_for_decay

    factor: float = 1.0
    _success_streak: int = 0

    def on_error(self):
        self.factor = min(self.max_factor, self.factor * self.grow)
        self._success_streak = 0

    def on_success(self):
        self._success_streak += 1
        if self._success_streak >= self.successes_for_decay:
            self.factor = max(self.min_factor, self.factor / self.decay)
            self._success_streak = 0

    def compute_delay(self, base_delay: float, jitter: float = app_constants.throttle_jitter) -> float:
        j = random.uniform(-jitter, jitter)
        return max(0.0, (base_delay + j) * self.factor)


@dataclass
class CircuitBreaker:
    fail_threshold: int = app_constants.breaker_fail_threshold
    window_size: int = app_constants.breaker_window_size
    error_rate_threshold: float = app_constants.breaker_error_rate_threshold
    cooldown_seconds: int = app_constants.breaker_cooldown_seconds
    probe_interval_seconds: int = app_constants.breaker_probe_interval_seconds

    failures: int = 0
    total: int = 0
    state: str = "closed"  # closed | open | half-open
    _opened_at: float | None = None
    _last_probe: float | None = None

    def on_result(self, success: bool):
        self.total = min(self.window_size, self.total + 1)
        if success:
            if self.state == "half-open":
                # Success during half-open → close
                self.state = "closed"
                self.failures = 0
                self.total = 0
            else:
                # closed: decay counters
                self.failures = max(0, self.failures - 1)
        else:
            self.failures += 1
            # Open if hard threshold
            if self.failures >= self.fail_threshold and self.state != "open":
                self._open()
            # Or error rate over window
            elif (
                self.total >= self.window_size
                and (self.failures / self.total) >= self.error_rate_threshold
                and self.state != "open"
            ):
                self._open()

    def _open(self):
        self.state = "open"
        self._opened_at = time.time()
        self._last_probe = None

    def should_pause(self) -> bool:
        if self.state == "closed":
            return False
        now = time.time()
        if self.state == "open":
            # Cooldown fully
            if self._opened_at and (now - self._opened_at) >= self.cooldown_seconds:
                # allow probe
                self.state = "half-open"
                self._last_probe = None
                return False
            # still in cooldown; but allow spaced probes
            if self._last_probe is None or (now - self._last_probe) >= self.probe_interval_seconds:
                self.state = "half-open"
                self._last_probe = now
                return False
            return True
        # half-open: allow request; next on_result decides state
        return False


# Shared instances used by scrapers
adaptive = AdaptiveBackoff()
breaker = CircuitBreaker()

# Runtime override to adjust speed without restart
_speed_mode: str = "normal"  # normal | fast | slow
_scale_override: float | None = None


def _current_scale() -> float:
    if _scale_override is not None:
        return _scale_override
    return app_constants.throttle_scale


def throttle_before_request(base_delay: float = 1.0) -> None:
    # Circuit breaker: pause if needed
    while breaker.should_pause():
        time.sleep(1)
    # Adaptive backoff delay with jitter
    delay = adaptive.compute_delay(base_delay * _current_scale())
    _check_delay(delay)


def reset_throttling() -> None:
    """Reset adaptive backoff and circuit breaker to defaults."""
    adaptive.factor = app_constants.adaptive_min_factor
    adaptive._success_streak = 0
    breaker.failures = 0
    breaker.total = 0
    breaker.state = "closed"
    breaker._opened_at = None
    breaker._last_probe = None


def set_speed_mode(mode: str) -> dict:
    """Set global speed mode: 'fast' | 'slow' | 'normal'. Returns state.

    - fast: lower throttle scale (env FAST_THROTTLE_SCALE)
    - slow: higher throttle scale (env SLOW_THROTTLE_SCALE)
    - normal: use THROTTLE_SCALE from env
    Resets adaptive/breaker state on change.
    """
    global _speed_mode, _scale_override
    mode = (mode or "").strip().lower()
    if mode not in ("fast", "slow", "normal"):
        raise ValueError("mode must be one of: fast, slow, normal")
    _speed_mode = mode
    if mode == "fast":
        _scale_override = app_constants.fast_throttle_scale
    elif mode == "slow":
        _scale_override = app_constants.slow_throttle_scale
    else:
        _scale_override = None
    reset_throttling()
    return get_speed_mode()


def get_speed_mode() -> dict:
    return {
        "mode": _speed_mode,
        "scale": _current_scale(),
        "adaptive_factor": adaptive.factor,
        "breaker_state": breaker.state,
    }


def report_success():
    adaptive.on_success()
    breaker.on_result(True)


def report_failure():
    adaptive.on_error()
    breaker.on_result(False)
