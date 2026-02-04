"""Unit tests for request handler orchestration behavior."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.api.schemas import ResponseModel, RootResponse
from app.core.constants import RequestType
from app.core.errors import AppError
from app.services import request_handler


def _response(request_type: RequestType, status: str, message: str) -> ResponseModel:
    """Build a ResponseModel for test stubs."""
    return ResponseModel(request_type=request_type, status=status, message=message)


class RequestHandlerTests(unittest.TestCase):
    """Validate lock, queue, dispatch, and finalize semantics."""

    def setUp(self) -> None:
        request_handler._allow_context_modification = False
        self._status_patcher = patch("app.services.request_handler.publish_status", return_value=None)
        self._sync_patcher = patch("app.services.request_handler.sync_status_from_locks", return_value=None)
        self._status_patcher.start()
        self._sync_patcher.start()

    def tearDown(self) -> None:
        request_handler._allow_context_modification = False
        self._sync_patcher.stop()
        self._status_patcher.stop()

    @patch("app.services.request_handler.acquire_lock")
    def test_root_short_circuits_without_lock(self, acquire_lock) -> None:
        """Root request should bypass lock and pipeline orchestration."""
        model, status = request_handler.handle_request(RequestType.ROOT)
        self.assertEqual(status, 200)
        self.assertIsInstance(model, RootResponse)
        acquire_lock.assert_not_called()

    @patch("app.services.request_handler.acquire_lock", return_value=False)
    def test_busy_when_lock_unavailable_and_not_modifiable(self, _acquire_lock) -> None:
        """When lock is unavailable and local modification is disabled, return BUSY."""
        model, status = request_handler.handle_request(RequestType.SCRAPE)
        self.assertEqual(status, 503)
        self.assertEqual(model.status, "BUSY")
        self.assertFalse(request_handler._allow_context_modification)

    @patch("app.services.request_handler.enqueue_request", return_value=True)
    @patch("app.services.request_handler.acquire_lock", return_value=False)
    def test_queue_when_lock_unavailable_and_modification_allowed(self, _acquire_lock, enqueue_request) -> None:
        """When lock is unavailable but local process owns context gate, request is queued."""
        request_handler._allow_context_modification = True
        model, status = request_handler.handle_request(RequestType.MUSTS)
        self.assertEqual(status, 202)
        self.assertEqual(model.status, "REQUEST_QUEUED")
        enqueue_request.assert_called_once_with(RequestType.MUSTS)

    @patch("app.services.request_handler.enqueue_request", return_value=False)
    @patch("app.services.request_handler.acquire_lock", return_value=False)
    def test_queue_failed_when_enqueue_rejected(self, _acquire_lock, enqueue_request) -> None:
        """Queue failure should return QUEUE_FAILED when enqueue cannot accept request."""
        request_handler._allow_context_modification = True
        model, status = request_handler.handle_request(RequestType.MUSTS)
        self.assertEqual(status, 503)
        self.assertEqual(model.status, "QUEUE_FAILED")
        enqueue_request.assert_called_once_with(RequestType.MUSTS)

    @patch("app.services.request_handler.release_lock", return_value=True)
    @patch("app.services.request_handler.clear_downloaded_dir", return_value=0)
    @patch("app.services.request_handler.publish_context_state")
    @patch("app.services.request_handler.record_success")
    @patch("app.services.request_handler.record_failure")
    @patch("app.services.request_handler.run_scrape")
    @patch("app.services.request_handler.resolve_request", return_value=(True, RequestType.SCRAPE))
    @patch("app.services.request_handler.load_context_state")
    @patch("app.services.request_handler.acquire_lock", return_value=True)
    def test_scrape_from_queue_sets_extra_and_decrements_errors(
        self,
        _acquire_lock,
        _load_context_state,
        _resolve_request,
        run_scrape,
        record_failure,
        record_success,
        _publish_context_state,
        _clear_downloaded_dir,
        _release_lock,
    ) -> None:
        """Queued scrape response should carry from_queue extra and mark success decrement."""
        run_scrape.return_value = (_response(RequestType.SCRAPE, "DONE", "ok"), 200)

        model, status = request_handler.handle_request(RequestType.SCRAPE)

        self.assertEqual(status, 200)
        self.assertEqual(model.extra, {"from_queue": True})
        record_success.assert_called_once_with()
        record_failure.assert_not_called()

    @patch("app.services.request_handler.release_lock", return_value=True)
    @patch("app.services.request_handler.clear_downloaded_dir", return_value=0)
    @patch("app.services.request_handler.publish_context_state")
    @patch("app.services.request_handler.record_success")
    @patch("app.services.request_handler.record_failure")
    @patch("app.services.request_handler.run_musts")
    @patch("app.services.request_handler.resolve_request", return_value=(False, RequestType.MUSTS))
    @patch("app.services.request_handler.load_context_state")
    @patch("app.services.request_handler.acquire_lock", return_value=True)
    def test_server_error_increments_failure_counter(
        self,
        _acquire_lock,
        _load_context_state,
        _resolve_request,
        run_musts,
        record_failure,
        record_success,
        _publish_context_state,
        _clear_downloaded_dir,
        _release_lock,
    ) -> None:
        """500 pipeline response should trigger failure counter increment."""
        run_musts.return_value = (_response(RequestType.MUSTS, "ERROR", "boom"), 500)

        model, status = request_handler.handle_request(RequestType.MUSTS)

        self.assertEqual(status, 500)
        self.assertEqual(model.status, "ERROR")
        record_failure.assert_called_once_with()
        record_success.assert_not_called()

    @patch("app.services.request_handler.release_lock", return_value=True)
    @patch("app.services.request_handler.clear_downloaded_dir", return_value=0)
    @patch("app.services.request_handler.publish_context_state")
    @patch("app.services.request_handler.record_success")
    @patch("app.services.request_handler.record_failure")
    @patch("app.services.request_handler.resolve_request")
    @patch("app.services.request_handler.load_context_state")
    @patch("app.services.request_handler.acquire_lock", return_value=True)
    def test_context_suspended_exception_skips_error_counters(
        self,
        _acquire_lock,
        _load_context_state,
        resolve_request,
        record_failure,
        record_success,
        _publish_context_state,
        _clear_downloaded_dir,
        _release_lock,
    ) -> None:
        """CONTEXT_SUSPENDED should return 503 and avoid increment/decrement calls."""
        resolve_request.side_effect = AppError("AppContext is suspended", "CONTEXT_SUSPENDED")

        model, status = request_handler.handle_request(RequestType.MUSTS)

        self.assertEqual(status, 503)
        self.assertEqual(model.status, "CONTEXT_SUSPENDED")
        record_failure.assert_not_called()
        record_success.assert_not_called()


if __name__ == "__main__":
    unittest.main()
