"""Unit tests for API schemas."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pydantic import ValidationError

from app.api.schemas import AdminKeyResult, AdminRequest, AdminResponse, ResponseModel, RootResponse
from app.core.constants import AdminAction, RequestType


class ApiSchemasTests(unittest.TestCase):
    """Validate model constraints and serialization behavior."""

    @patch("app.api.schemas.get_settings")
    def test_root_response_builds_payload_from_settings(self, get_settings_mock: MagicMock) -> None:
        """RootResponse should construct root payload from current settings."""
        get_settings_mock.return_value = SimpleNamespace(
            APP_NAME="robotdegilim",
            ADMIN_EMAIL="admin@example.com",
            APP_DESCRIPTION="desc",
            APP_VERSION="1.2.3",
        )

        model = RootResponse()

        self.assertEqual(model.root["app_name"], "robotdegilim")
        self.assertEqual(model.root["admin_email"], "admin@example.com")
        self.assertEqual(model.root["description"], "desc")
        self.assertEqual(model.root["version"], "1.2.3")
        self.assertIn("root", model.root["endpoints"])
        self.assertIn("scrape", model.root["endpoints"])
        self.assertIn("musts", model.root["endpoints"])
        self.assertIn("admin", model.root["endpoints"])

    def test_response_model_accepts_valid_request_type(self) -> None:
        """ResponseModel should accept valid RequestType enum values."""
        model = ResponseModel(
            request_type=RequestType.SCRAPE,
            status="SUCCESS",
            message="ok",
            extra={"from_queue": True},
        )

        self.assertEqual(model.request_type, RequestType.SCRAPE)
        self.assertEqual(model.extra, {"from_queue": True})

    def test_response_model_rejects_invalid_request_type(self) -> None:
        """ResponseModel should reject unsupported request_type strings."""
        with self.assertRaises(ValidationError):
            ResponseModel(
                request_type="invalid",
                status="FAILED",
                message="bad",
            )

    def test_admin_request_ignores_extra_fields(self) -> None:
        """AdminRequest should ignore unknown extra fields by schema config."""
        model = AdminRequest(
            action=AdminAction.SETTINGS_GET,
            payload={"x": 1},
            ignored_field="ignored",
        )

        dumped = model.model_dump()
        self.assertEqual(dumped["action"], AdminAction.SETTINGS_GET)
        self.assertEqual(dumped["payload"], {"x": 1})
        self.assertNotIn("ignored_field", dumped)

    def test_admin_request_rejects_unknown_action(self) -> None:
        """AdminRequest should reject unknown action names."""
        with self.assertRaises(ValidationError):
            AdminRequest(action="not_a_real_action")

    def test_admin_response_serializes_action_enum_as_string_in_json_mode(self) -> None:
        """AdminResponse should serialize action enum correctly for API responses."""
        model = AdminResponse(
            action=AdminAction.ADMIN_LOCK_STATUS,
            status="SUCCESS",
            message="ok",
            data={"locked": False},
        )

        dumped = model.model_dump(mode="json")
        self.assertEqual(dumped["action"], "admin_lock_status")
        self.assertEqual(dumped["data"], {"locked": False})

    def test_admin_key_result_requires_required_fields(self) -> None:
        """AdminKeyResult should require both ok and message fields."""
        model = AdminKeyResult(ok=True, message="updated")
        self.assertTrue(model.ok)
        self.assertEqual(model.message, "updated")

        with self.assertRaises(ValidationError):
            AdminKeyResult(ok=True)


if __name__ == "__main__":
    unittest.main()
