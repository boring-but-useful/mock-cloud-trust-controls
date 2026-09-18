from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def copy_project(tmp_path: Path) -> Path:
    project_copy = tmp_path / "mock_cloud_trust_controls"
    ignore = shutil.ignore_patterns(
        ".git",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "venv",
    )
    shutil.copytree(PROJECT_ROOT, project_copy, ignore=ignore)
    return project_copy


def run_validator(
    project_root: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/validate_controls.py", *arguments],
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
            self.assertIn("Validated 10 controls", result.stdout)
            self.assertIn("Validated 13 evidence items", result.stdout)
            self.assertIn("Validated 4 exceptions", result.stdout)

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

    def test_validate_controls_rejects_unknown_evidence_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            evidence = load_yaml(evidence_path)
            evidence["evidence_items"][0]["provider"] = "azure"
            write_yaml(evidence_path, evidence)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "provider 'azure' is not allowed; expected one of: aws, gcp, common",
                result.stdout,
            )

    def test_validate_controls_rejects_unknown_evidence_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            evidence = load_yaml(evidence_path)
            evidence["evidence_items"][0]["environment"] = "qa"
            write_yaml(evidence_path, evidence)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "environment 'qa' is not allowed; expected one of: "
                "production, shared, staging",
                result.stdout,
            )

    def test_validate_controls_rejects_unknown_evidence_source_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            control_path = project_copy / "controls" / "MCTC-LOG-01.yaml"
            control = load_yaml(control_path)
            control["evidence_sources"][0]["provider"] = "other"
            write_yaml(control_path, control)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "evidence_sources[1] provider 'other' is not allowed",
                result.stdout,
            )

    def test_validate_controls_rejects_invalid_resource_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            evidence = load_yaml(evidence_path)
            evidence["evidence_items"][0]["resource_ref"] = []
            write_yaml(evidence_path, evidence)

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "field 'resource_ref' must be a non-empty str",
                result.stdout,
            )

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
            self.assertIn("Validated 4 exceptions", result.stdout)

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

    def test_validate_controls_reports_invalid_yaml_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            control_path = project_copy / "controls" / "MCTC-IAM-01.yaml"
            control_path.write_text("control_id: [", encoding="utf-8")

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn("MCTC-IAM-01.yaml: invalid YAML", result.stdout)
            self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_validate_controls_reports_missing_input_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            (project_copy / "examples" / "mock_evidence.yaml").unlink()

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "mock_evidence.yaml: unable to read file",
                result.stdout,
            )
            self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_as_of_date_and_strict_warnings_are_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))

            normal = run_validator(project_copy, "--as-of", "2026-12-15")
            strict = run_validator(
                project_copy,
                "--as-of",
                "2026-12-15",
                "--strict-warnings",
            )

            self.assertEqual(normal.returncode, 0)
            self.assertIn("expires in 16 days", normal.stdout)
            self.assertEqual(strict.returncode, 1)
            self.assertIn("--strict-warnings was set", strict.stdout)

    def test_invalid_as_of_date_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))

            result = run_validator(project_copy, "--as-of", "September-1")

            self.assertEqual(result.returncode, 2)
            self.assertIn("must be an ISO date", result.stderr)


if __name__ == "__main__":
    unittest.main()
