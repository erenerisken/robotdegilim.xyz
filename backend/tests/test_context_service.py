"""Unit tests for context service dual-store and queue behavior."""

from __future__ import annotations

import shutil
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.context import service
from app.core.constants import CONTEXT_KEY, RequestType
from app.core.errors import AppError


class ContextServiceTests(unittest.TestCase):
    """Validate run/admin context isolation and orchestration semantics."""

    def setUp(self) -> None:
        base_tmp = Path(__file__).resolve().parent / ".tmp"
        base_tmp.mkdir(parents=True, exist_ok=True)
        self.tmp_dir = base_tmp / f"context_{uuid.uuid4().hex}"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        self._patches: list[patch] = []
        self._patches.append(
            patch(
                "app.context.service.downloaded_path",
                side_effect=lambda filename: self.tmp_dir / "downloaded" / filename,
            )
        )
        self._patches.append(
            patch(
                "app.context.service.staged_path",
                side_effect=lambda filename: self.tmp_dir / "staged" / filename,
            )
        )
        self._patches.append(
            patch(
                "app.context.service.published_path",
                side_effect=lambda filename: self.tmp_dir / "published" / filename,
            )
        )
        self._patches.append(patch("app.context.service.s3_file_exists", return_value=False))
        self._patches.append(patch("app.context.service.download_file", side_effect=lambda *args, **kwargs: "ok"))
        self._patches.append(patch("app.context.service.upload_file", side_effect=lambda *args, **kwargs: "ok"))
        self._patches.append(patch("app.context.service.move_file", side_effect=lambda src, dst: str(dst)))
        self._patches.append(patch("app.context.service.read_json", return_value={}))
        self._patches.append(patch("app.context.service.log_item"))
        self._patches.append(
            patch(
                "app.context.service.get_settings",
                return_value=SimpleNamespace(CONTEXT_MAX_ERRORS=2),
            )
        )

        for patcher in self._patches:
            patcher.start()

        service.detach_context(admin=False)
        service.detach_context(admin=True)

    def tearDown(self) -> None:
        service.detach_context(admin=False)
        service.detach_context(admin=True)
        for patcher in reversed(self._patches):
            patcher.stop()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_run_and_admin_stores_are_isolated(self) -> None:
        """Mutating run context should not alter admin context store."""
        service.load_context_state(admin=False)
        service.load_context_state(admin=True)

        self.assertTrue(service.enqueue_request(RequestType.MUSTS, admin=False))
        run_snapshot = service.get_context_snapshot(admin=False)
        admin_snapshot = service.get_context_snapshot(admin=True)

        self.assertEqual(run_snapshot["queue"], [RequestType.MUSTS.value])
        self.assertEqual(admin_snapshot["queue"], [])

    def test_detach_admin_does_not_clear_run_store(self) -> None:
        """Detaching admin store should leave run store intact."""
        service.load_context_state(admin=False)
        service.load_context_state(admin=True)
        self.assertTrue(service.enqueue_request(RequestType.MUSTS, admin=False))

        service.detach_context(admin=True)

        run_snapshot = service.get_context_snapshot(admin=False)
        self.assertEqual(run_snapshot["queue"], [RequestType.MUSTS.value])

    def test_resolve_request_uses_queue_then_falls_back(self) -> None:
        """Resolve should consume queued request first, then incoming request."""
        service.load_context_state(admin=False)
        self.assertTrue(service.enqueue_request(RequestType.MUSTS, admin=False))

        from_queue, request_type = service.resolve_request(RequestType.SCRAPE, admin=False)
        self.assertTrue(from_queue)
        self.assertEqual(request_type, RequestType.MUSTS)

        from_queue, request_type = service.resolve_request(RequestType.SCRAPE, admin=False)
        self.assertFalse(from_queue)
        self.assertEqual(request_type, RequestType.SCRAPE)

    def test_publish_context_state_uses_admin_upload_guard(self) -> None:
        """Admin publish should call upload_file with _admin=True."""
        with patch("app.context.service.upload_file", return_value="ok") as upload_mock:
            service.load_context_state(admin=True)
            self.assertTrue(service.enqueue_request(RequestType.MUSTS, admin=True))

            service.publish_context_state(admin=True)

            upload_mock.assert_called_once()
            call_args = upload_mock.call_args
            self.assertEqual(call_args.kwargs["_admin"], True)
            self.assertEqual(call_args.args[1], CONTEXT_KEY)

    def test_record_failure_suspends_and_unsuspend_resets_gate(self) -> None:
        """Failure threshold should suspend; unsuspend should allow queue ops again."""
        service.load_context_state(admin=False)

        service.record_failure(admin=False)
        snapshot = service.get_context_snapshot(admin=False)
        self.assertEqual(snapshot["error_count"], 1)
        self.assertFalse(snapshot["suspended"])

        service.record_failure(admin=False)
        snapshot = service.get_context_snapshot(admin=False)
        self.assertEqual(snapshot["error_count"], 0)
        self.assertTrue(snapshot["suspended"])

        with self.assertRaises(AppError) as exc:
            service.enqueue_request(RequestType.MUSTS, admin=False)
        self.assertEqual(exc.exception.code, "CONTEXT_SUSPENDED")

        service.unsuspend_processing(admin=False)
        self.assertTrue(service.enqueue_request(RequestType.MUSTS, admin=False))


if __name__ == "__main__":
    unittest.main()
