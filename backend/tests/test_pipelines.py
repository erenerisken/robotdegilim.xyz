"""Unit tests for musts and NTE pipeline orchestrators."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.core.constants import RequestType
from app.core.errors import AppError
from app.pipelines.musts import run_musts
from app.pipelines.nte_available import run_nte_available


class MustsPipelineTests(unittest.TestCase):
    """Validate musts pipeline success and failure control flow."""

    @patch("app.pipelines.musts.run_nte_list", side_effect=AppError("nte fail", "NTE_LIST_FAIL"))
    @patch("app.pipelines.musts.upload_file")
    @patch("app.pipelines.musts.move_file")
    @patch("app.pipelines.musts.write_json")
    @patch("app.pipelines.musts.extract_dept_node", return_value={1: ["CENG101"]})
    @patch("app.pipelines.musts.get_department_catalog_page")
    @patch("app.pipelines.musts.load_departments")
    @patch("app.pipelines.musts.CacheStore")
    @patch("app.pipelines.musts.get_settings")
    @patch("app.pipelines.musts.log_item")
    def test_run_musts_success_even_if_nte_post_step_fails(
        self,
        _log_item,
        get_settings,
        cache_store_cls,
        load_departments,
        get_department_catalog_page,
        _extract_dept_node,
        _write_json,
        _move_file,
        upload_file,
        _run_nte_list,
    ) -> None:
        """Musts should still succeed when best-effort NTE post-step fails."""
        get_settings.return_value = SimpleNamespace(MUSTS_PARSER_VERSION="1.0.0")
        cache = MagicMock()
        cache.get.return_value = None
        cache_store_cls.return_value = cache
        load_departments.return_value = {
            "571": {"p": "CENG"},
            "999": {"p": "<prefix-not-found>"},
        }
        get_department_catalog_page.return_value = ("k", "h", SimpleNamespace(text="<html/>"))

        model, status = run_musts()

        self.assertEqual(status, 200)
        self.assertEqual(model.request_type, RequestType.MUSTS)
        self.assertEqual(model.status, "SUCCESS")
        upload_file.assert_called_once()
        cache.flush.assert_called_once()

    @patch("app.pipelines.musts.log_item")
    @patch("app.pipelines.musts.load_departments")
    @patch("app.pipelines.musts.CacheStore")
    @patch("app.pipelines.musts.get_settings")
    def test_run_musts_dependency_error_returns_503(
        self,
        _get_settings,
        _cache_store,
        load_departments,
        _log_item,
    ) -> None:
        """Dependency failures should map to 503 and user-safe message."""
        load_departments.side_effect = AppError("download failed", "DOWNLOAD_DEPARTMENTS_FAILED")

        model, status = run_musts()

        self.assertEqual(status, 503)
        self.assertEqual(model.status, "FAILED")
        self.assertEqual(model.message, "Departments data could not be loaded from S3.")

    @patch("app.pipelines.musts.log_item")
    @patch("app.pipelines.musts.load_departments", return_value={})
    @patch("app.pipelines.musts.CacheStore")
    @patch("app.pipelines.musts.get_settings", return_value=SimpleNamespace(MUSTS_PARSER_VERSION="1.0.0"))
    def test_run_musts_no_output_returns_500(
        self,
        _get_settings,
        cache_store_cls,
        _load_departments,
        _log_item,
    ) -> None:
        """No generated musts data should fail with generic 500 response."""
        cache = MagicMock()
        cache_store_cls.return_value = cache

        model, status = run_musts()

        self.assertEqual(status, 500)
        self.assertEqual(model.status, "FAILED")
        self.assertEqual(model.message, "Musts process failed, see the error logs for details.")


class NteAvailablePipelineTests(unittest.TestCase):
    """Validate nte_available pipeline output and error paths."""

    @patch("app.pipelines.nte_available.upload_file")
    @patch("app.pipelines.nte_available.move_file")
    @patch("app.pipelines.nte_available.write_json")
    @patch("app.pipelines.nte_available.build_course_output")
    @patch("app.pipelines.nte_available.build_available_index")
    @patch("app.pipelines.nte_available.extract_nte_courses")
    @patch("app.pipelines.nte_available.load_dependencies")
    @patch("app.pipelines.nte_available.log_item")
    def test_run_nte_available_success(
        self,
        _log_item,
        load_dependencies,
        extract_nte_courses,
        build_available_index,
        build_course_output,
        _write_json,
        _move_file,
        upload_file,
    ) -> None:
        """NTE available should publish when dependencies and matches exist."""
        deps = {
            "departments": {"CENG": {}},
            "nte_list": {"CENG": []},
            "data": {"dummy": []},
        }
        load_dependencies.return_value = deps
        nte_courses: list[dict[str, str]] = []

        def fill_nte_courses(_nte_list, output):
            output.extend([{"code": "CENG 101", "credits": "4"}])

        extract_nte_courses.side_effect = fill_nte_courses
        build_available_index.return_value = {
            "CENG101": {"numeric": 101, "name": "Intro"},
        }
        build_course_output.return_value = {"code": {"departmental": "CENG101"}, "name": "Intro"}

        output_path = run_nte_available()

        self.assertTrue(output_path.endswith("nteAvailable.json"))
        upload_file.assert_called_once()

    @patch("app.pipelines.nte_available.log_item")
    @patch("app.pipelines.nte_available.load_dependencies")
    @patch("app.pipelines.nte_available.extract_nte_courses")
    @patch("app.pipelines.nte_available.build_available_index", return_value={})
    def test_run_nte_available_no_available_index_raises(
        self,
        _build_available_index,
        extract_nte_courses,
        load_dependencies,
        _log_item,
    ) -> None:
        """Empty available index should raise AppError with expected code."""
        load_dependencies.return_value = {"departments": {}, "nte_list": {}, "data": {}}
        extract_nte_courses.side_effect = lambda _a, out: out.extend([{"code": "CENG 101", "credits": "4"}])

        with self.assertRaises(AppError) as exc:
            run_nte_available()
        self.assertEqual(exc.exception.code, "NTE_AVAILABLE_NO_COURSES")

    @patch("app.pipelines.nte_available.log_item")
    @patch("app.pipelines.nte_available.load_dependencies")
    @patch("app.pipelines.nte_available.extract_nte_courses")
    @patch("app.pipelines.nte_available.build_available_index")
    def test_run_nte_available_no_matching_output_raises(
        self,
        build_available_index,
        extract_nte_courses,
        load_dependencies,
        _log_item,
    ) -> None:
        """No matching course output after filtering should raise explicit error."""
        load_dependencies.return_value = {"departments": {}, "nte_list": {}, "data": {}}
        extract_nte_courses.side_effect = lambda _a, out: out.extend([{"code": "ABCD 999", "credits": "3"}])
        build_available_index.return_value = {"CENG101": {"numeric": 101, "name": "Intro"}}

        with self.assertRaises(AppError) as exc:
            run_nte_available()
        self.assertEqual(exc.exception.code, "NTE_AVAILABLE_NO_NTE_COURSES")


if __name__ == "__main__":
    unittest.main()
