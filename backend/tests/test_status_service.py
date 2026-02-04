"""Unit tests for status publishing service."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.services.status_service import compute_status_from_locks, publish_status, sync_status_from_locks


class StatusServiceTests(unittest.TestCase):
    """Validate busy/idle computation and status payload writes."""

    @patch("app.services.status_service.run_lock_exists", return_value=True)
    @patch("app.services.status_service.admin_lock_exists", return_value=False)
    def test_compute_status_busy_when_run_lock_active(self, _admin_lock_exists, _run_lock_exists) -> None:
        """Run lock should force busy status."""
        self.assertEqual(compute_status_from_locks(), "busy")

    @patch("app.services.status_service.run_lock_exists", return_value=False)
    @patch("app.services.status_service.admin_lock_exists", return_value=True)
    def test_compute_status_busy_when_admin_lock_active(self, _admin_lock_exists, _run_lock_exists) -> None:
        """Admin lock should force busy status."""
        self.assertEqual(compute_status_from_locks(), "busy")

    @patch("app.services.status_service.run_lock_exists", return_value=False)
    @patch("app.services.status_service.admin_lock_exists", return_value=False)
    def test_compute_status_idle_when_no_locks(self, _admin_lock_exists, _run_lock_exists) -> None:
        """No active locks should produce idle status."""
        self.assertEqual(compute_status_from_locks(), "idle")

    @patch("app.services.status_service.write_json_payload")
    def test_publish_status_writes_public_payload(self, write_json_payload) -> None:
        """Status writer should publish public status payload with updated timestamp."""
        publish_status("busy")

        write_json_payload.assert_called_once()
        key = write_json_payload.call_args.args[0]
        payload = write_json_payload.call_args.args[1]
        self.assertEqual(key, "status.json")
        self.assertEqual(payload["status"], "busy")
        self.assertIn("updated_at", payload)
        self.assertTrue(write_json_payload.call_args.kwargs.get("public_read"))

    @patch("app.services.status_service.publish_status")
    @patch("app.services.status_service.compute_status_from_locks", return_value="idle")
    def test_sync_status_from_locks_publishes_computed_value(
        self,
        _compute_status_from_locks,
        publish_status_mock,
    ) -> None:
        """Sync helper should publish the computed lock-derived status."""
        sync_status_from_locks()
        publish_status_mock.assert_called_once_with("idle")


if __name__ == "__main__":
    unittest.main()

