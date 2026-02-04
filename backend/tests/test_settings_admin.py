"""Unit tests for admin settings read/update helpers."""

from __future__ import annotations

import shutil
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services import settings_admin


class SettingsAdminTests(unittest.TestCase):
    """Validate masking, per-key outcomes, and .env update behavior."""

    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / ".tmp"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.tmp_dir = base_tmp / f"settings_{uuid.uuid4().hex}"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.env_path = self.tmp_dir / ".env"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    @patch("app.services.settings_admin.get_settings")
    def test_get_public_settings_masks_sensitive_keys(self, get_settings_mock: MagicMock) -> None:
        """Public settings payload should hide sensitive values but keep key names."""
        fake_settings = SimpleNamespace(
            model_dump=lambda: {
                "APP_NAME": "robotdegilim",
                "MAIL_USERNAME": "user@example.com",
                "MAIL_PASSWORD": "secret",
                "ADMIN_SECRET": "super-secret",
                "S3_LOCK_OWNER_ID": "owner-123",
                "HTTP_TIMEOUT": 15,
            }
        )
        get_settings_mock.return_value = fake_settings

        result = settings_admin.get_public_settings()

        self.assertEqual(result["APP_NAME"], "robotdegilim")
        self.assertEqual(result["HTTP_TIMEOUT"], 15)
        self.assertEqual(result["MAIL_USERNAME"], "***")
        self.assertEqual(result["MAIL_PASSWORD"], "***")
        self.assertEqual(result["ADMIN_SECRET"], "***")
        self.assertEqual(result["S3_LOCK_OWNER_ID"], "***")

    def test_encode_env_value_formats_supported_types(self) -> None:
        """Value encoder should produce stable .env-safe string representations."""
        self.assertEqual(settings_admin._encode_env_value(True), "true")
        self.assertEqual(settings_admin._encode_env_value(False), "false")
        self.assertEqual(settings_admin._encode_env_value(42), "42")
        self.assertEqual(settings_admin._encode_env_value("abc"), "abc")
        self.assertEqual(settings_admin._encode_env_value("hello world"), '"hello world"')
        self.assertEqual(settings_admin._encode_env_value('a"b'), '"a\\"b"')

    def test_update_env_file_preserves_comments_and_unrelated_lines(self) -> None:
        """Updater should only change targeted keys and keep unrelated file content."""
        self.env_path.write_text(
            "# comment\nHTTP_TIMEOUT=10\nKEEP_THIS=1\n\n",
            encoding="utf-8",
        )

        settings_admin._update_env_file(
            self.env_path,
            {"HTTP_TIMEOUT": "20", "LOG_LEVEL": "DEBUG"},
        )

        content = self.env_path.read_text(encoding="utf-8")
        self.assertIn("# comment", content)
        self.assertIn("HTTP_TIMEOUT=20", content)
        self.assertIn("KEEP_THIS=1", content)
        self.assertIn("LOG_LEVEL=DEBUG", content)

    @patch("app.services.settings_admin._settings_env_path")
    @patch("app.services.settings_admin.get_settings")
    def test_apply_settings_updates_reports_per_key_results_and_counts(
        self,
        get_settings_mock: MagicMock,
        settings_env_path_mock: MagicMock,
    ) -> None:
        """Updater should report key-level outcomes and update .env for valid keys."""
        settings_env_path_mock.return_value = self.env_path
        self.env_path.write_text("# base\nHTTP_TIMEOUT=10\n", encoding="utf-8")

        get_settings_mock.return_value = SimpleNamespace()

        updates = {
            "HTTP_TIMEOUT": 25,       # valid
            "LOG_LEVEL": "DEBUG",     # valid known key, appended if missing
            "ADMIN_SECRET": "x",      # blocked
            "UNKNOWN_KEY": "x",       # unknown
            "S3_LOCK_TIMEOUT_SECONDS": "abc",  # invalid (expects int)
        }

        results, applied_count, failed_count = settings_admin.apply_settings_updates(updates)

        self.assertEqual(results["HTTP_TIMEOUT"]["ok"], True)
        self.assertEqual(results["LOG_LEVEL"]["ok"], True)
        self.assertEqual(results["ADMIN_SECRET"]["ok"], False)
        self.assertEqual(results["UNKNOWN_KEY"]["ok"], False)
        self.assertEqual(results["S3_LOCK_TIMEOUT_SECONDS"]["ok"], False)

        self.assertEqual(applied_count, 2)
        self.assertEqual(failed_count, 3)

        content = self.env_path.read_text(encoding="utf-8")
        self.assertIn("HTTP_TIMEOUT=25", content)
        self.assertIn("LOG_LEVEL=DEBUG", content)
        self.assertIn("# base", content)

        get_settings_mock.cache_clear.assert_called_once_with()
        self.assertGreaterEqual(get_settings_mock.call_count, 1)

    @patch("app.services.settings_admin._settings_env_path")
    @patch("app.services.settings_admin.get_settings")
    def test_apply_settings_updates_skips_reload_when_nothing_applied(
        self,
        get_settings_mock: MagicMock,
        settings_env_path_mock: MagicMock,
    ) -> None:
        """Updater should not touch cache reload path when all updates fail."""
        settings_env_path_mock.return_value = self.env_path
        self.env_path.write_text("HTTP_TIMEOUT=10\n", encoding="utf-8")

        updates = {
            "UNKNOWN_KEY": "x",
            "ADMIN_SECRET": "secret",
            "S3_LOCK_TIMEOUT_SECONDS": "not-an-int",
        }
        results, applied_count, failed_count = settings_admin.apply_settings_updates(updates)

        self.assertEqual(applied_count, 0)
        self.assertEqual(failed_count, 3)
        self.assertFalse(results["UNKNOWN_KEY"]["ok"])
        self.assertFalse(results["ADMIN_SECRET"]["ok"])
        self.assertFalse(results["S3_LOCK_TIMEOUT_SECONDS"]["ok"])

        get_settings_mock.cache_clear.assert_not_called()


if __name__ == "__main__":
    unittest.main()
