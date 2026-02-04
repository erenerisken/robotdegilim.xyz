"""Unit tests for HTTP utility helpers."""

from __future__ import annotations

import logging
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.core.errors import AppError
from app.utils import http


def _http_settings(
    *,
    timeout: float = 5.0,
    retries: int = 3,
    base_delay: float = 0.01,
    jitter: float = 0.01,
    throttle: bool = False,
    headers: dict[str, str] | None = None,
) -> SimpleNamespace:
    """Build a lightweight settings stub for HTTP tests."""
    return SimpleNamespace(
        HTTP_TIMEOUT=timeout,
        GLOBAL_RETRIES=retries,
        RETRY_BASE_DELAY=base_delay,
        RETRY_JITTER=jitter,
        THROTTLE_ENABLED=throttle,
        DEFAULT_HEADERS=headers or {},
    )


class HttpUtilsTests(unittest.TestCase):
    """Validate retry, session, and wrapper behavior in app.utils.http."""

    def setUp(self) -> None:
        http.reset_session()

    def tearDown(self) -> None:
        http.reset_session()

    @patch("app.utils.http.requests.Session")
    @patch("app.utils.http.get_settings")
    def test_get_session_caches_single_instance_and_applies_headers(
        self,
        get_settings_mock: MagicMock,
        session_cls_mock: MagicMock,
    ) -> None:
        """get_session should build once and reuse the same configured session."""
        get_settings_mock.return_value = _http_settings(headers={"User-Agent": "ua-test"})
        session = MagicMock()
        session.headers = {}
        session_cls_mock.return_value = session

        first = http.get_session()
        second = http.get_session()

        self.assertIs(first, second)
        session_cls_mock.assert_called_once()
        self.assertEqual(session.headers["User-Agent"], "ua-test")

    @patch("app.utils.http.requests.Session")
    @patch("app.utils.http.get_settings")
    def test_get_session_ignores_non_dict_headers(
        self,
        get_settings_mock: MagicMock,
        session_cls_mock: MagicMock,
    ) -> None:
        """get_session should ignore default headers when not dict-shaped."""
        settings = _http_settings(headers={})
        settings.DEFAULT_HEADERS = "not-a-dict"
        get_settings_mock.return_value = settings
        session = MagicMock()
        session.headers = {"Existing": "1"}
        session_cls_mock.return_value = session

        http.get_session()

        self.assertEqual(session.headers, {"Existing": "1"})

    @patch("app.utils.http._sleep_with_jitter")
    @patch("app.utils.http.get_session")
    @patch("app.utils.http.get_settings")
    def test_request_returns_on_first_ok_response(
        self,
        get_settings_mock: MagicMock,
        get_session_mock: MagicMock,
        sleep_mock: MagicMock,
    ) -> None:
        """request should return immediately on successful status code."""
        get_settings_mock.return_value = _http_settings()
        response = MagicMock(status_code=200)
        session = MagicMock()
        session.request.return_value = response
        get_session_mock.return_value = session

        result = http.request("GET", "https://example.com")

        self.assertIs(result, response)
        sleep_mock.assert_not_called()
        session.request.assert_called_once()

    @patch("app.utils.http._sleep_with_jitter")
    @patch("app.utils.http.get_session")
    @patch("app.utils.http.get_settings")
    def test_request_retries_after_exception_then_succeeds(
        self,
        get_settings_mock: MagicMock,
        get_session_mock: MagicMock,
        sleep_mock: MagicMock,
    ) -> None:
        """request should retry network exceptions until a successful response."""
        get_settings_mock.return_value = _http_settings(retries=3)
        response = MagicMock(status_code=200)
        session = MagicMock()
        session.request.side_effect = [RuntimeError("net"), response]
        get_session_mock.return_value = session

        result = http.request("GET", "https://example.com")

        self.assertIs(result, response)
        self.assertEqual(session.request.call_count, 2)
        sleep_mock.assert_called_once()

    @patch("app.utils.http._sleep_with_jitter")
    @patch("app.utils.http.get_session")
    @patch("app.utils.http.get_settings")
    def test_request_retries_retryable_status_then_succeeds(
        self,
        get_settings_mock: MagicMock,
        get_session_mock: MagicMock,
        sleep_mock: MagicMock,
    ) -> None:
        """request should retry on retryable HTTP statuses like 5xx."""
        get_settings_mock.return_value = _http_settings(retries=3)
        retryable = MagicMock(status_code=503)
        ok = MagicMock(status_code=200)
        session = MagicMock()
        session.request.side_effect = [retryable, ok]
        get_session_mock.return_value = session

        result = http.request("GET", "https://example.com")

        self.assertIs(result, ok)
        self.assertEqual(session.request.call_count, 2)
        sleep_mock.assert_called_once()

    @patch("app.utils.http._sleep_with_jitter")
    @patch("app.utils.http.get_session")
    @patch("app.utils.http.get_settings")
    def test_request_non_retryable_status_raises_immediately(
        self,
        get_settings_mock: MagicMock,
        get_session_mock: MagicMock,
        sleep_mock: MagicMock,
    ) -> None:
        """request should fail fast on non-retryable status codes (e.g. 404)."""
        get_settings_mock.return_value = _http_settings(retries=3)
        response = MagicMock(status_code=404)
        session = MagicMock()
        session.request.return_value = response
        get_session_mock.return_value = session

        with self.assertRaises(AppError) as ctx:
            http.request("GET", "https://example.com")

        self.assertEqual(ctx.exception.code, "HTTP_REQUEST_FAILED")
        self.assertEqual(ctx.exception.context["status_code"], 404)
        sleep_mock.assert_not_called()
        session.request.assert_called_once()

    @patch("app.utils.http._sleep_with_jitter")
    @patch("app.utils.http.get_session")
    @patch("app.utils.http.get_settings")
    def test_request_gives_up_after_retries_and_preserves_last_cause(
        self,
        get_settings_mock: MagicMock,
        get_session_mock: MagicMock,
        sleep_mock: MagicMock,
    ) -> None:
        """request should raise giving-up AppError with the last exception as cause."""
        get_settings_mock.return_value = _http_settings(retries=2)
        session = MagicMock()
        session.request.side_effect = [RuntimeError("first"), RuntimeError("last")]
        get_session_mock.return_value = session

        with self.assertRaises(AppError) as ctx:
            http.request("GET", "https://example.com")

        self.assertEqual(ctx.exception.code, "HTTP_REQUEST_FAILED")
        self.assertEqual(str(ctx.exception.cause), "last")
        self.assertEqual(session.request.call_count, 2)
        self.assertEqual(sleep_mock.call_count, 2)

    @patch("app.utils.http.request")
    def test_get_wraps_non_apperror(self, request_mock: MagicMock) -> None:
        """get should wrap unexpected exceptions with GET_REQUEST_FAILED."""
        request_mock.side_effect = ValueError("bad")

        with self.assertRaises(AppError) as ctx:
            http.get("https://example.com")

        self.assertEqual(ctx.exception.code, "GET_REQUEST_FAILED")
        self.assertIsInstance(ctx.exception.cause, ValueError)

    @patch("app.utils.http.request")
    def test_get_passes_through_apperror(self, request_mock: MagicMock) -> None:
        """get should re-raise AppError without wrapping again."""
        original = AppError("x", "X")
        request_mock.side_effect = original

        with self.assertRaises(AppError) as ctx:
            http.get("https://example.com")

        self.assertIs(ctx.exception, original)

    @patch("app.utils.http.request")
    def test_post_wraps_non_apperror(self, request_mock: MagicMock) -> None:
        """post should wrap unexpected exceptions with POST_REQUEST_FAILED."""
        request_mock.side_effect = RuntimeError("post bad")

        with self.assertRaises(AppError) as ctx:
            http.post("https://example.com", data={"a": 1})

        self.assertEqual(ctx.exception.code, "POST_REQUEST_FAILED")
        self.assertIsInstance(ctx.exception.cause, RuntimeError)

    def test_should_retry_rules(self) -> None:
        """_should_retry should handle None, 429, and 5xx as retryable."""
        self.assertTrue(http._should_retry(None))
        self.assertTrue(http._should_retry(429))
        self.assertTrue(http._should_retry(500))
        self.assertTrue(http._should_retry(599))
        self.assertFalse(http._should_retry(404))
        self.assertFalse(http._should_retry(400))

    @patch("app.utils.http.time.sleep")
    @patch("app.utils.http.random.uniform")
    def test_sleep_with_jitter_uses_non_negative_delay(
        self,
        uniform_mock: MagicMock,
        sleep_mock: MagicMock,
    ) -> None:
        """_sleep_with_jitter should never sleep a negative duration."""
        uniform_mock.return_value = -5.0

        http._sleep_with_jitter(base_delay=0.1, jitter=0.5, attempt=1)

        sleep_mock.assert_called_once_with(0.0)

    @patch("app.utils.http.get_settings")
    def test_maybe_throttle_swallows_settings_errors(self, get_settings_mock: MagicMock) -> None:
        """_maybe_throttle should not raise even when settings access fails."""
        get_settings_mock.side_effect = RuntimeError("settings failed")

        http._maybe_throttle()

    @patch("app.utils.http.get_settings")
    def test_maybe_throttle_noop_when_enabled(self, get_settings_mock: MagicMock) -> None:
        """_maybe_throttle should remain no-op until throttle logic is implemented."""
        get_settings_mock.return_value = _http_settings(throttle=True)

        http._maybe_throttle()


if __name__ == "__main__":
    unittest.main()
