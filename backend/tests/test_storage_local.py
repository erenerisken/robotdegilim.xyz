"""Unit tests for local storage helpers."""

from __future__ import annotations

import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from app.core.errors import AppError
from app.storage import local


class LocalStorageTests(unittest.TestCase):
    """Validate filesystem helpers under app.storage.local."""

    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / ".tmp"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.tmp_dir = base_tmp / f"local_{uuid.uuid4().hex}"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_read_json_missing_returns_empty_dict(self) -> None:
        """read_json should return {} when file does not exist."""
        result = local.read_json(self.tmp_dir / "missing.json")
        self.assertEqual(result, {})

    def test_read_json_non_dict_returns_empty_dict(self) -> None:
        """read_json should return {} for valid JSON values that are not objects."""
        path = self.tmp_dir / "list.json"
        path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

        result = local.read_json(path)
        self.assertEqual(result, {})

    def test_read_json_invalid_json_raises_app_error(self) -> None:
        """read_json should raise AppError when JSON decoding fails."""
        path = self.tmp_dir / "invalid.json"
        path.write_text("{not-json", encoding="utf-8")

        with self.assertRaises(AppError) as ctx:
            local.read_json(path)

        self.assertEqual(ctx.exception.code, "READ_JSON_FAILED")

    def test_write_json_creates_parent_and_writes_payload(self) -> None:
        """write_json should create parent dirs and persist payload."""
        path = self.tmp_dir / "nested" / "data.json"
        payload = {"a": 1, "b": "x"}

        returned = local.write_json(path, payload)

        self.assertEqual(returned, str(path))
        self.assertTrue(path.exists())
        written = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(written, payload)

    def test_move_file_success(self) -> None:
        """move_file should move existing file and return destination path."""
        src = self.tmp_dir / "src.txt"
        dst = self.tmp_dir / "out" / "dst.txt"
        src.write_text("hello", encoding="utf-8")

        returned = local.move_file(src, dst)

        self.assertEqual(returned, str(dst))
        self.assertFalse(src.exists())
        self.assertEqual(dst.read_text(encoding="utf-8"), "hello")

    def test_move_file_missing_source_raises(self) -> None:
        """move_file should raise AppError when source is missing."""
        src = self.tmp_dir / "missing.txt"
        dst = self.tmp_dir / "dst.txt"

        with self.assertRaises(AppError) as ctx:
            local.move_file(src, dst)

        self.assertEqual(ctx.exception.code, "MOVE_FILE_FAILED")

    def test_delete_file_returns_true_when_deleted(self) -> None:
        """delete_file should return True when a file is removed."""
        path = self.tmp_dir / "delete-me.txt"
        path.write_text("x", encoding="utf-8")

        deleted = local.delete_file(path)

        self.assertTrue(deleted)
        self.assertFalse(path.exists())

    def test_delete_file_returns_false_when_missing(self) -> None:
        """delete_file should return False for missing files."""
        deleted = local.delete_file(self.tmp_dir / "missing.txt")
        self.assertFalse(deleted)

    @patch("app.storage.local.downloaded_dir")
    def test_clear_downloaded_dir_removes_nested_entries(self, downloaded_dir_mock) -> None:
        """clear_downloaded_dir should remove all nested files/directories."""
        root = self.tmp_dir / "downloaded"
        nested = root / "a" / "b"
        nested.mkdir(parents=True, exist_ok=True)
        (root / "root.txt").write_text("1", encoding="utf-8")
        (nested / "leaf.txt").write_text("2", encoding="utf-8")
        downloaded_dir_mock.return_value = root

        removed = local.clear_downloaded_dir()

        # Entries removed: root.txt, leaf.txt, b dir, a dir
        self.assertEqual(removed, 4)
        self.assertTrue(root.exists())
        self.assertEqual(list(root.iterdir()), [])

    @patch("app.storage.local.downloaded_dir")
    def test_clear_downloaded_dir_missing_returns_zero(self, downloaded_dir_mock) -> None:
        """clear_downloaded_dir should return 0 when root folder is absent."""
        downloaded_dir_mock.return_value = self.tmp_dir / "no-such-dir"

        removed = local.clear_downloaded_dir()

        self.assertEqual(removed, 0)


if __name__ == "__main__":
    unittest.main()
