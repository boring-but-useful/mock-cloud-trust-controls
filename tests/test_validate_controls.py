from __future__ import annotations

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
            control = yaml.safe_load(control_path.read_text(encoding="utf-8"))
            del control["owner"]
            control_path.write_text(
                yaml.safe_dump(control, sort_keys=False),
                encoding="utf-8",
            )

            result = run_validator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn("Validation failed:", result.stdout)
            self.assertIn(
                "MCTC-IAM-01.yaml: missing required field 'owner'",
                result.stdout,
            )


if __name__ == "__main__":
    unittest.main()
