"""Unit tests for AppError and logging helpers."""

from __future__ import annotations

import json
import logging
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.core.constants import LOGGER_APP
from app.core.errors import AppError
from app.core.logging import _JsonFormatter, _build_formatter, log_item


class AppErrorTests(unittest.TestCase):
    """Validate AppError payload and logging behavior."""

    def test_to_log_includes_optional_fields(self) -> None:
        """to_log should include code/context/cause when present."""
        err = AppError(
            message="Something failed",
            code="X_FAILED",
            context={"id": 1},
            cause=ValueError("bad value"),
        )
        payload = err.to_log(include_stack=True)

        self.assertEqual(payload["message"], "Something failed")
        self.assertEqual(payload["code"], "X_FAILED")
        self.assertEqual(payload["context"], {"id": 1})
        self.assertEqual(payload["cause"], "bad value")
        self.assertIn("stack", payload)

    def test_log_uses_cause_traceback_when_available(self) -> None:
        """AppError.log should pass cause traceback via exc_info."""
        try:
            raise ValueError("boom")
        except ValueError as cause:
            err = AppError("Top-level failure", cause=cause)

        logger = MagicMock(spec=logging.Logger)
        err.log(logger, logging.ERROR)

        args, kwargs = logger.log.call_args
        self.assertEqual(args[0], logging.ERROR)

        payload = json.loads(args[1])
        self.assertEqual(payload["message"], "Top-level failure")
        self.assertEqual(payload["cause"], "boom")
        self.assertNotIn("stack", payload)

        exc_info = kwargs["exc_info"]
        self.assertIsNotNone(exc_info)
        self.assertIs(exc_info[0], ValueError)
        self.assertIsInstance(exc_info[1], ValueError)

    def test_log_adds_stack_when_no_traceback_available(self) -> None:
        """AppError.log should include stack text when traceback is unavailable."""
        err = AppError("No traceback case")
        logger = MagicMock(spec=logging.Logger)

        err.log(logger, logging.ERROR)

        args, kwargs = logger.log.call_args
        payload = json.loads(args[1])
        self.assertIn("stack", payload)
        self.assertIsNone(kwargs["exc_info"])


class LoggingHelperTests(unittest.TestCase):
    """Validate helper-level behavior in app.core.logging."""

    @patch("app.core.logging.logging.getLogger")
    def test_log_item_falls_back_to_app_logger_for_unknown_name(self, get_logger_mock: MagicMock) -> None:
        """log_item should use app logger for unknown logger names."""
        logger = MagicMock(spec=logging.Logger)
        get_logger_mock.return_value = logger

        log_item("unknown_logger", logging.INFO, "hello")

        get_logger_mock.assert_called_once_with(LOGGER_APP)
        logger.log.assert_called_once_with(logging.INFO, "hello", exc_info=None, stack_info=False, extra=None)

    @patch("app.core.logging.logging.getLogger")
    def test_log_item_delegates_to_apperror_log(self, get_logger_mock: MagicMock) -> None:
        """log_item should call AppError.log for AppError payloads."""
        logger = MagicMock(spec=logging.Logger)
        get_logger_mock.return_value = logger
        err = AppError("delegated")

        with patch.object(err, "log") as err_log_mock:
            log_item(LOGGER_APP, logging.ERROR, err)

        err_log_mock.assert_called_once_with(logger, logging.ERROR)

    @patch("app.core.logging.logging.getLogger")
    def test_log_item_wraps_internal_logger_failure(self, get_logger_mock: MagicMock) -> None:
        """log_item should wrap logger failures with LOGGING_FAILED AppError."""
        logger = MagicMock(spec=logging.Logger)
        logger.log.side_effect = RuntimeError("write failed")
        get_logger_mock.return_value = logger

        with self.assertRaises(AppError) as ctx:
            log_item(LOGGER_APP, logging.INFO, "x")

        self.assertEqual(ctx.exception.code, "LOGGING_FAILED")

    @patch("app.core.logging.get_settings")
    def test_build_formatter_returns_json_formatter_when_enabled(self, get_settings_mock: MagicMock) -> None:
        """_build_formatter should return JSON formatter when LOG_JSON is true."""
        get_settings_mock.return_value = SimpleNamespace(LOG_JSON=True)

        formatter = _build_formatter()
        self.assertIsInstance(formatter, _JsonFormatter)

    @patch("app.core.logging.get_settings")
    def test_build_formatter_returns_standard_formatter_when_disabled(self, get_settings_mock: MagicMock) -> None:
        """_build_formatter should return standard formatter when LOG_JSON is false."""
        get_settings_mock.return_value = SimpleNamespace(LOG_JSON=False)

        formatter = _build_formatter()
        self.assertIsInstance(formatter, logging.Formatter)
        self.assertNotIsInstance(formatter, _JsonFormatter)

    def test_json_formatter_outputs_expected_shape(self) -> None:
        """_JsonFormatter should emit parseable JSON with expected fields."""
        formatter = _JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=123,
            msg="hello",
            args=(),
            exc_info=None,
        )

        payload = json.loads(formatter.format(record))
        self.assertEqual(payload["level"], "INFO")
        self.assertEqual(payload["logger"], "test")
        self.assertEqual(payload["msg"], "hello")
        self.assertIn("ts", payload)


if __name__ == "__main__":
    unittest.main()
