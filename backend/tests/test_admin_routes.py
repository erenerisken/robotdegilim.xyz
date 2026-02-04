"""Route-function tests for /admin wiring without HTTP client dependency."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.api.routes import run_admin_action
from app.api.schemas import AdminRequest, AdminResponse
from app.core.constants import AdminAction
from app.core.errors import AppError


def _response_json(response: object) -> dict:
    """Decode JSON payload from Starlette JSONResponse."""
    body = getattr(response, "body", b"{}")
    return json.loads(body.decode("utf-8"))


class AdminRoutesTests(unittest.TestCase):
    """Validate auth mapping and handler dispatch wiring in admin route."""

    @patch("app.api.routes.verify_admin_secret")
    def test_admin_auth_not_configured_returns_503(self, verify_admin_secret) -> None:
        """Route should map missing configured secret to HTTP 503."""
        verify_admin_secret.side_effect = AppError(
            "Admin secret is not configured.",
            "ADMIN_SECRET_NOT_CONFIGURED",
        )
        body = AdminRequest(action=AdminAction.ADMIN_LOCK_STATUS, payload=None)

        response = run_admin_action(body, x_admin_secret="any", x_admin_lock_token=None)
        payload = _response_json(response)

        self.assertEqual(response.status_code, 503)
        self.assertEqual(payload["status"], "FAILED")
        self.assertEqual(payload["action"], "admin_lock_status")

    @patch("app.api.routes.verify_admin_secret")
    def test_admin_auth_failed_returns_401(self, verify_admin_secret) -> None:
        """Route should map invalid secret to HTTP 401."""
        verify_admin_secret.side_effect = AppError("Invalid admin secret.", "ADMIN_AUTH_FAILED")
        body = AdminRequest(action=AdminAction.ADMIN_LOCK_STATUS, payload=None)

        response = run_admin_action(body, x_admin_secret="bad", x_admin_lock_token=None)
        payload = _response_json(response)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload["status"], "FAILED")

    @patch("app.api.routes.verify_admin_secret", return_value=None)
    @patch("app.api.routes.handle_admin_action")
    def test_admin_route_forwards_body_and_token(self, handle_admin_action, _verify_admin_secret) -> None:
        """Route should forward parsed action/payload/token to handler."""
        handle_admin_action.return_value = (
            AdminResponse(
                action=AdminAction.SETTINGS_GET,
                status="SUCCESS",
                message="ok",
                data={"settings": {"A": "***"}},
            ),
            200,
        )
        body = AdminRequest.model_validate(
            {
                "action": "settings_get",
                "payload": {"x": 1},
                "extra_ignored": "value",
            }
        )

        response = run_admin_action(
            body,
            x_admin_secret="secret",
            x_admin_lock_token="lock-token-1",
        )
        payload = _response_json(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["action"], "settings_get")
        self.assertEqual(payload["status"], "SUCCESS")

        called_action, called_payload, called_token = handle_admin_action.call_args.args
        self.assertEqual(called_action, AdminAction.SETTINGS_GET)
        self.assertEqual(called_payload, {"x": 1})
        self.assertEqual(called_token, "lock-token-1")

    @patch("app.api.routes.verify_admin_secret", return_value=None)
    @patch("app.api.routes.handle_admin_action")
    def test_admin_route_serializes_enum_action_as_string(
        self,
        handle_admin_action,
        _verify_admin_secret,
    ) -> None:
        """Response should serialize enum action to plain string."""
        handle_admin_action.return_value = (
            AdminResponse(
                action=AdminAction.ADMIN_LOCK_STATUS,
                status="SUCCESS",
                message="status",
                data={"active": False},
            ),
            200,
        )
        body = AdminRequest(action=AdminAction.ADMIN_LOCK_STATUS, payload=None)

        response = run_admin_action(body, x_admin_secret="secret", x_admin_lock_token=None)
        payload = _response_json(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["action"], "admin_lock_status")

    def test_admin_request_rejects_unknown_action(self) -> None:
        """Schema should reject unknown admin action values."""
        with self.assertRaises(ValidationError):
            AdminRequest.model_validate({"action": "unknown_action"})


if __name__ == "__main__":
    unittest.main()
