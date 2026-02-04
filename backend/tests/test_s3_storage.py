"""Unit tests for S3 mock storage lock and mutation behavior."""

from __future__ import annotations

import unittest
import uuid
import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.core.errors import AppError
from app.core.constants import S3_ADMIN_LOCK_FILE, S3_ADMIN_OP_LOCK_FILE
from app.storage import s3


class S3StorageTests(unittest.TestCase):
    """Validate run/admin lock semantics and guarded S3 mutations."""

    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / ".tmp"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.mock_dir = base_tmp / f"s3_{uuid.uuid4().hex}"
        self.mock_dir.mkdir(parents=True, exist_ok=True)

        self.mock_settings = SimpleNamespace(
            S3_LOCK_OWNER_ID="test-owner",
            S3_LOCK_TIMEOUT_SECONDS=60 * 60,
            ADMIN_LOCK_TIMEOUT_SECONDS=3 * 60 * 60,
        )

        self._patch_mock_dir = patch("app.storage.s3.common._mock_dir", return_value=self.mock_dir)
        self._patch_settings = patch("app.storage.s3.common.get_settings", return_value=self.mock_settings)
        self._patch_mock_dir.start()
        self._patch_settings.start()
        s3._set_run_lock_held_for_tests(False)

    def tearDown(self) -> None:
        s3._set_run_lock_held_for_tests(False)
        self._patch_settings.stop()
        self._patch_mock_dir.stop()
        shutil.rmtree(self.mock_dir, ignore_errors=True)

    def test_run_lock_acquire_and_release(self) -> None:
        self.assertTrue(s3.acquire_lock())
        self.assertTrue(s3.release_lock())

    def test_run_lock_blocked_while_admin_lock_active(self) -> None:
        acquired = s3.admin_acquire_lock()
        self.assertTrue(acquired.get("acquired"))
        self.assertFalse(s3.acquire_lock())

    def test_admin_lock_acquire_returns_token_and_status(self) -> None:
        result = s3.admin_acquire_lock()
        self.assertTrue(result["acquired"])
        self.assertIsInstance(result["token"], str)
        self.assertTrue(result["status"]["active"])
        self.assertNotIn("token", result["status"])

    def test_admin_lock_validate_token(self) -> None:
        result = s3.admin_acquire_lock()
        token = result["token"]
        self.assertTrue(s3.admin_validate_lock_token(token))
        self.assertFalse(s3.admin_validate_lock_token("wrong-token"))
        self.assertFalse(s3.admin_validate_lock_token(None))

    def test_admin_op_lock_requires_valid_token(self) -> None:
        self.assertFalse(s3.admin_acquire_op_lock("nope"))

        token = s3.admin_acquire_lock()["token"]
        self.assertTrue(s3.admin_acquire_op_lock(token))
        self.assertFalse(s3.admin_acquire_op_lock(token))

    def test_admin_release_blocked_while_op_lock_active(self) -> None:
        token = s3.admin_acquire_lock()["token"]
        self.assertTrue(s3.admin_acquire_op_lock(token))
        self.assertFalse(s3.admin_release_lock(token))

    def test_stale_op_lock_is_invalid_without_admin_lock(self) -> None:
        token = s3.admin_acquire_lock()["token"]
        self.assertTrue(s3.admin_acquire_op_lock(token))
        (self.mock_dir / S3_ADMIN_LOCK_FILE).unlink(missing_ok=True)

        self.assertFalse(s3.admin_op_lock_exists())
        self.assertFalse((self.mock_dir / S3_ADMIN_OP_LOCK_FILE).exists())

    def test_upload_requires_run_lock(self) -> None:
        src = self.mock_dir / "source.txt"
        src.write_text("data", encoding="utf-8")
        with self.assertRaises(AppError) as exc:
            s3.upload_file(src, "files/out.txt")
        self.assertEqual(exc.exception.code, "LOCK_NOT_ACQUIRED")

    def test_upload_with_run_lock_succeeds(self) -> None:
        src = self.mock_dir / "source.txt"
        src.write_text("data", encoding="utf-8")
        self.assertTrue(s3.acquire_lock())

        out = s3.upload_file(src, "files/out.txt")
        self.assertTrue(Path(out).exists())
        self.assertEqual((self.mock_dir / "files" / "out.txt").read_text(encoding="utf-8"), "data")

    def test_upload_run_blocked_by_admin_lock(self) -> None:
        src = self.mock_dir / "source.txt"
        src.write_text("data", encoding="utf-8")
        self.assertTrue(s3.acquire_lock())
        s3.admin_acquire_lock()

        with self.assertRaises(AppError) as exc:
            s3.upload_file(src, "files/out.txt")
        self.assertEqual(exc.exception.code, "OPERATION_BLOCKED_ADMIN_LOCK")

    def test_admin_upload_requires_op_lock(self) -> None:
        src = self.mock_dir / "source.txt"
        src.write_text("data", encoding="utf-8")
        token = s3.admin_acquire_lock()["token"]

        with self.assertRaises(AppError) as exc:
            s3.upload_file(src, "files/out.txt", _admin=True)
        self.assertEqual(exc.exception.code, "ADMIN_OP_LOCK_NOT_ACQUIRED")

        self.assertTrue(s3.admin_acquire_op_lock(token))
        out = s3.upload_file(src, "files/out.txt", _admin=True)
        self.assertTrue(Path(out).exists())

    def test_download_allowed_while_admin_lock_active(self) -> None:
        file_path = self.mock_dir / "files" / "src.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("payload", encoding="utf-8")
        s3.admin_acquire_lock()

        out_path = self.mock_dir / "local" / "downloaded.txt"
        s3.download_file("files/src.txt", out_path)
        self.assertEqual(out_path.read_text(encoding="utf-8"), "payload")

    def test_s3_file_exists_invalid_key_returns_false(self) -> None:
        self.assertFalse(s3.s3_file_exists("../escape.txt"))

    def test_delete_requires_lock(self) -> None:
        with self.assertRaises(AppError) as exc:
            s3.delete_file("files/any.txt")
        self.assertEqual(exc.exception.code, "LOCK_NOT_ACQUIRED")


if __name__ == "__main__":
    unittest.main()
