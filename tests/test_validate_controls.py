from __future__ import annotations

from datetime import date, timedelta
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def copy_project(tmp_path: Path) -> Path:
    project_copy = tmp_path / "mock_cloud_trust_controls"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__")
    shutil.copytree(PROJECT_ROOT, project_copy, ignore=ignore)
    return project_copy


def run_validator(project_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/validate_controls.py"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


class ValidateControlsTests(unittest.TestCase):
    def test_validate_controls_passes_current_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 0)
            self.assertIn("Validated 7 controls", result.stdout)
            self.assertIn("Validated 7 evidence items", result.stdout)
            self.assertIn("Validated 3 exceptions", result.stdout)

    def test_validate_controls_reports_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            control_path = project_copy / "controls" / "MCTC-IAM-01.yaml"
            control = load_yaml(control_path)
            del control["owner"]
            write_yaml(control_path, control)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Validation failed:", result.stdout)
            self.assertIn(
                "MCTC-IAM-01.yaml: missing required field 'owner'",
                result.stdout,
            )

    def test_validate_controls_rejects_unknown_evidence_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            evidence = load_yaml(evidence_path)
            evidence["evidence_items"][0]["status"] = "mostly_passes"
            write_yaml(evidence_path, evidence)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn("status 'mostly_passes' is not allowed", result.stdout)

    def test_validate_controls_rejects_malformed_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            evidence = load_yaml(evidence_path)
            evidence["evidence_items"][0]["collection_date"] = "July 15, 2026"
            write_yaml(evidence_path, evidence)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "field 'collection_date' must be an ISO date (YYYY-MM-DD)",
                result.stdout,
            )

    def test_validate_controls_rejects_invalid_field_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            exceptions_path = project_copy / "examples" / "mock_exceptions.yaml"
            exceptions = load_yaml(exceptions_path)
            exceptions["exceptions"][0]["owner"] = ["Security", "IT"]
            write_yaml(exceptions_path, exceptions)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "exceptions[1] field 'owner' must be str",
                result.stdout,
            )

    def test_validate_controls_rejects_approved_expired_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            exceptions_path = project_copy / "examples" / "mock_exceptions.yaml"
            exceptions = load_yaml(exceptions_path)
            exceptions["exceptions"][0]["expires_on"] = "2000-01-01"
            exceptions["exceptions"][0]["status"] = "approved"
            write_yaml(exceptions_path, exceptions)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "approved exception expired on 2000-01-01; set status to 'expired'",
                result.stdout,
            )

    def test_validate_controls_warns_for_exception_expiring_soon(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            exceptions_path = project_copy / "examples" / "mock_exceptions.yaml"
            exceptions = load_yaml(exceptions_path)
            expires_on = date.today() + timedelta(days=10)
            exceptions["exceptions"][0]["expires_on"] = expires_on.isoformat()
            exceptions["exceptions"][0]["status"] = "approved"
            write_yaml(exceptions_path, exceptions)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 0)
            self.assertIn("Validation warnings:", result.stdout)
            self.assertIn(
                f"approved exception expires in 10 days on {expires_on.isoformat()}",
                result.stdout,
            )
            self.assertIn("Validated 3 exceptions", result.stdout)

    def test_exception_expiry_warning_window_boundaries(self) -> None:
        for days_remaining, warning_expected in ((0, True), (30, True), (31, False)):
            with self.subTest(days_remaining=days_remaining):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    project_copy = copy_project(Path(tmp_dir))
                    exceptions_path = (
                        project_copy / "examples" / "mock_exceptions.yaml"
                    )
                    exceptions = load_yaml(exceptions_path)
                    expires_on = date.today() + timedelta(days=days_remaining)
                    exceptions["exceptions"][0]["expires_on"] = (
                        expires_on.isoformat()
                    )
                    exceptions["exceptions"][0]["status"] = "approved"
                    write_yaml(exceptions_path, exceptions)

                    result = run_validator(project_copy)

                    self.assertEqual(result.returncode, 0)
                    if warning_expected:
                        self.assertIn("Validation warnings:", result.stdout)
                    else:
                        self.assertNotIn("Validation warnings:", result.stdout)

    def test_validate_controls_rejects_invalid_evidence_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            write_yaml(evidence_path, {"evidence_items": {"not": "a list"}})

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "mock_evidence.yaml: 'evidence_items' must be a list",
                result.stdout,
            )


if __name__ == "__main__":
    unittest.main()
