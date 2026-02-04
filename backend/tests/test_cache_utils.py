"""Unit tests for cache utilities and CacheStore behavior."""

from __future__ import annotations

import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.core.errors import AppError
from app.utils import cache


class CacheUtilsTests(unittest.TestCase):
    """Validate helpers in app.utils.cache."""

    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / ".tmp"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.tmp_dir = base_tmp / f"cache_{uuid.uuid4().hex}"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_make_key_is_stable_for_dict_order(self) -> None:
        """make_key should be deterministic regardless of input dict order."""
        key_a = cache.make_key(
            "GET",
            "https://example.com",
            params={"b": 2, "a": 1},
        )
        key_b = cache.make_key(
            "GET",
            "https://example.com",
            params={"a": 1, "b": 2},
        )
        self.assertEqual(key_a, key_b)

    def test_make_key_handles_unserializable_values_via_str(self) -> None:
        """make_key should not fail for non-JSON-native values."""
        class _Obj:
            def __str__(self) -> str:
                return "custom"

        key = cache.make_key("POST", "https://example.com", data={"x": _Obj()})
        self.assertIn("custom", key)

    def test_hash_content_accepts_str_and_bytes_like(self) -> None:
        """hash_content should support str/bytes/bytearray/memoryview consistently."""
        h1 = cache.hash_content("abc")
        h2 = cache.hash_content(b"abc")
        h3 = cache.hash_content(bytearray(b"abc"))
        h4 = cache.hash_content(memoryview(b"abc"))

        self.assertEqual(h1, h2)
        self.assertEqual(h2, h3)
        self.assertEqual(h3, h4)
        self.assertEqual(len(h1), 64)

    def test_hash_content_rejects_none(self) -> None:
        """hash_content should reject None input."""
        with self.assertRaises(AppError) as ctx:
            cache.hash_content(None)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "HASH_CONTENT_FAILED")

    def test_hash_content_rejects_invalid_type(self) -> None:
        """hash_content should reject unsupported input types."""
        with self.assertRaises(AppError) as ctx:
            cache.hash_content(123)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "HASH_CONTENT_FAILED")

    def test_load_cache_returns_empty_for_missing_invalid_or_non_dict(self) -> None:
        """_load_cache should safely return empty dict for invalid states."""
        missing = self.tmp_dir / "missing.json"
        self.assertEqual(cache._load_cache(missing), {})

        invalid = self.tmp_dir / "invalid.json"
        invalid.write_text("{bad", encoding="utf-8")
        self.assertEqual(cache._load_cache(invalid), {})

        non_dict = self.tmp_dir / "list.json"
        non_dict.write_text(json.dumps([1, 2]), encoding="utf-8")
        self.assertEqual(cache._load_cache(non_dict), {})

    def test_save_cache_writes_json_payload(self) -> None:
        """_save_cache should write JSON and create missing parent dirs."""
        path = self.tmp_dir / "nested" / "cache.json"
        payload = {"k": {"hash": "h", "parser_version": "v", "parsed": {"x": 1}}}

        cache._save_cache(payload, path)

        self.assertTrue(path.exists())
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), payload)

    @patch("pathlib.Path.write_text", side_effect=OSError("disk full"))
    def test_save_cache_wraps_write_errors(self, _: MagicMock) -> None:
        """_save_cache should wrap write failures with SAVE_CACHE_FAILED."""
        with self.assertRaises(AppError) as ctx:
            cache._save_cache({}, self.tmp_dir / "cache.json")
        self.assertEqual(ctx.exception.code, "SAVE_CACHE_FAILED")


class CacheStoreTests(unittest.TestCase):
    """Validate lazy loading, matching logic, and flush behavior."""

    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / ".tmp"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.tmp_dir = base_tmp / f"cache_store_{uuid.uuid4().hex}"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.tmp_dir / "store.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_get_lazy_loads_then_returns_none_on_missing_entry(self) -> None:
        """get should lazily load cache file and return None for missing entry."""
        store = cache.CacheStore(path=self.path, parser_version="v1")
        self.assertIsNone(store.get("x", "h"))
        self.assertTrue(store._loaded)

    def test_set_and_get_hit_with_matching_hash_and_version(self) -> None:
        """Entry should be returned only when parser version and hash match."""
        store = cache.CacheStore(path=self.path, parser_version="v1")
        store.set("key", "hash-1", {"result": 1})

        self.assertEqual(store.get("key", "hash-1"), {"result": 1})

    def test_get_miss_on_version_mismatch(self) -> None:
        """Version mismatch should invalidate cached parsed payload."""
        self.path.write_text(
            json.dumps(
                {
                    "key": {
                        "hash": "h1",
                        "parser_version": "v-old",
                        "parsed": {"x": 1},
                    }
                }
            ),
            encoding="utf-8",
        )
        store = cache.CacheStore(path=self.path, parser_version="v-new")
        self.assertIsNone(store.get("key", "h1"))

    def test_get_miss_on_hash_mismatch(self) -> None:
        """Hash mismatch should invalidate cached parsed payload."""
        self.path.write_text(
            json.dumps(
                {
                    "key": {
                        "hash": "h1",
                        "parser_version": "v1",
                        "parsed": {"x": 1},
                    }
                }
            ),
            encoding="utf-8",
        )
        store = cache.CacheStore(path=self.path, parser_version="v1")
        self.assertIsNone(store.get("key", "h2"))

    def test_flush_writes_loaded_cache(self) -> None:
        """flush should persist in-memory cache when loaded."""
        store = cache.CacheStore(path=self.path, parser_version="v1")
        store.set("k", "h", {"a": 1})

        store.flush()

        disk = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertIn("k", disk)
        self.assertEqual(disk["k"]["hash"], "h")

    def test_flush_is_noop_when_not_loaded(self) -> None:
        """flush should do nothing when store has not been loaded."""
        store = cache.CacheStore(path=self.path, parser_version="v1")
        store.flush()
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
