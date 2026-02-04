"""Unit tests for core settings helpers."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core import settings as settings_module


class CoreSettingsTests(unittest.TestCase):
    """Validate Settings model and helper accessor behavior."""

    def setUp(self) -> None:
        settings_module.get_settings.cache_clear()

    def tearDown(self) -> None:
        settings_module.get_settings.cache_clear()

    def test_default_headers_factory_returns_expected_keys(self) -> None:
        """Default headers factory should return the expected outbound header keys."""
        headers = settings_module._default_headers_factory()
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept", headers)
        self.assertIn("Accept-Language", headers)

    def test_default_headers_factory_returns_new_dict_each_call(self) -> None:
        """Header factory should not share mutable dict instances across calls."""
        first = settings_module._default_headers_factory()
        second = settings_module._default_headers_factory()
        first["X-Test"] = "1"
        self.assertNotIn("X-Test", second)

    def test_get_settings_is_cached(self) -> None:
        """get_settings should return the same cached object until cache_clear."""
        one = settings_module.get_settings()
        two = settings_module.get_settings()
        self.assertIs(one, two)

    @patch.dict(
        os.environ,
        {
            "MAIL_USERNAME": "sender@example.com",
            "MAIL_SENDER": "",
            "MAIL_RECIPIENT": "",
            "ADMIN_EMAIL": "admin@example.com",
        },
        clear=False,
    )
    def test_get_settings_fills_mail_sender_and_recipient_defaults(self) -> None:
        """Missing mail sender/recipient should be derived from username/admin email."""
        settings_module.get_settings.cache_clear()
        s = settings_module.get_settings()

        self.assertEqual(s.MAIL_SENDER, "sender@example.com")
        self.assertEqual(s.MAIL_RECIPIENT, "admin@example.com")

    @patch.dict(
        os.environ,
        {
            "HTTP_TIMEOUT": "33",
            "GLOBAL_RETRIES": "7",
            "RETRY_BASE_DELAY": "1.5",
            "THROTTLE_ENABLED": "true",
        },
        clear=False,
    )
    def test_settings_parses_env_types(self) -> None:
        """Settings model should coerce env strings into typed fields."""
        settings_module.get_settings.cache_clear()
        s = settings_module.get_settings()

        self.assertEqual(s.HTTP_TIMEOUT, 33)
        self.assertEqual(s.GLOBAL_RETRIES, 7)
        self.assertAlmostEqual(s.RETRY_BASE_DELAY, 1.5)
        self.assertTrue(s.THROTTLE_ENABLED)

    def test_get_setting_returns_existing_and_default_for_missing(self) -> None:
        """get_setting should fetch known values and fallback for unknown keys."""
        timeout = settings_module.get_setting("HTTP_TIMEOUT")
        missing = settings_module.get_setting("NO_SUCH_SETTING", "fallback")

        self.assertIsInstance(timeout, int)
        self.assertEqual(missing, "fallback")

    def test_get_path_returns_path_and_handles_missing(self) -> None:
        """get_path should convert values to Path and return None when absent."""
        data_path = settings_module.get_path("DATA_DIR")
        missing = settings_module.get_path("NO_SUCH_PATH")
        fallback = settings_module.get_path("NO_SUCH_PATH", "tmp/fallback")

        self.assertIsInstance(data_path, Path)
        self.assertEqual(data_path, Path("data"))
        self.assertIsNone(missing)
        self.assertEqual(fallback, Path("tmp/fallback"))


if __name__ == "__main__":
    unittest.main()
