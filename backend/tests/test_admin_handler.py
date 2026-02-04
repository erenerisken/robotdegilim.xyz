"""Unit tests for admin action dispatcher behavior."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app.core.constants import AdminAction
from app.services.admin_handler import handle_admin_action


class AdminHandlerTests(unittest.TestCase):
    """Validate response flow for lock and mutating admin actions."""

    def setUp(self) -> None:
        self._status_patcher = patch("app.services.admin_handler.sync_status_from_locks", return_value=None)
        self._status_patcher.start()

    def tearDown(self) -> None:
        self._status_patcher.stop()

    @patch("app.services.admin_handler.admin_validate_lock_token", return_value=False)
    def test_mutating_action_requires_valid_token(self, _validate) -> None:
        model, status = handle_admin_action(AdminAction.CONTEXT_CLEAR_QUEUE, payload={})
        self.assertEqual(status, 409)
        self.assertEqual(model.status, "FAILED")

    @patch("app.services.admin_handler.admin_validate_lock_token", return_value=True)
    @patch("app.services.admin_handler.admin_acquire_op_lock", return_value=False)
    def test_mutating_action_rejects_when_op_lock_busy(self, _op_acquire, _validate) -> None:
        model, status = handle_admin_action(AdminAction.CONTEXT_CLEAR_QUEUE, payload={}, lock_token="t")
        self.assertEqual(status, 409)
        self.assertEqual(model.message, "Another admin operation is in progress.")

    @patch("app.services.admin_handler.admin_acquire_lock")
    def test_admin_lock_acquire_success_returns_token(self, acquire_lock) -> None:
        acquire_lock.return_value = {
            "acquired": True,
            "token": "abc-token",
            "status": {"active": True, "owner": "x"},
        }
        model, status = handle_admin_action(AdminAction.ADMIN_LOCK_ACQUIRE, payload=None)
        self.assertEqual(status, 200)
        self.assertEqual(model.status, "SUCCESS")
        self.assertEqual(model.data["lock_token"], "abc-token")

    @patch("app.services.admin_handler.admin_validate_lock_token", return_value=True)
    @patch("app.services.admin_handler.admin_op_lock_exists", return_value=True)
    def test_admin_release_blocked_while_operation_running(self, _op_exists, _validate) -> None:
        model, status = handle_admin_action(AdminAction.ADMIN_LOCK_RELEASE, payload=None, lock_token="t")
        self.assertEqual(status, 409)
        self.assertEqual(model.status, "FAILED")

    def test_settings_set_empty_payload_is_success(self) -> None:
        model, status = handle_admin_action(AdminAction.SETTINGS_SET, payload={"updates": {}})
        self.assertEqual(status, 409)  # mutating action without token

    @patch("app.services.admin_handler.admin_validate_lock_token", return_value=True)
    @patch("app.services.admin_handler.admin_acquire_op_lock", return_value=True)
    @patch("app.services.admin_handler.admin_release_op_lock")
    @patch("app.services.admin_handler.apply_settings_updates")
    def test_settings_set_partial_returns_207(
        self,
        apply_updates,
        _release,
        _op_acquire,
        _validate,
    ) -> None:
        apply_updates.return_value = (
            {
                "A": {"ok": True, "message": "updated"},
                "B": {"ok": False, "message": "blocked"},
            },
            1,
            1,
        )
        model, status = handle_admin_action(
            AdminAction.SETTINGS_SET,
            payload={"updates": {"A": "1", "B": "2"}},
            lock_token="t",
        )
        self.assertEqual(status, 207)
        self.assertEqual(model.status, "PARTIAL")
        self.assertEqual(model.data["applied_count"], 1)
        self.assertEqual(model.data["failed_count"], 1)


if __name__ == "__main__":
    unittest.main()
