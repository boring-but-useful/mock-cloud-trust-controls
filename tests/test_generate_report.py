from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def copy_project(tmp_path: Path) -> Path:
    project_copy = tmp_path / "mock_cloud_trust_controls"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__")
    shutil.copytree(PROJECT_ROOT, project_copy, ignore=ignore)
    return project_copy


class GenerateReportTests(unittest.TestCase):
    def test_generate_report_writes_expected_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            report_path = project_copy / "reports" / "sample_report.md"
            report_path.unlink()

            result = subprocess.run(
                [sys.executable, "scripts/generate_report.py"],
                cwd=project_copy,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "Wrote reports/sample_report.md")
            self.assertTrue(report_path.exists())

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("# Mock Cloud Trust Controls - Sample Report", report)
            self.assertIn("- Controls reviewed: 7", report)
            self.assertIn("- Evidence items: 7", report)
            self.assertIn("- Exceptions: 3", report)
            self.assertIn(
                "MCTC-VULN-01: Vulnerability Findings Are Triaged And Remediated",
                report,
            )


if __name__ == "__main__":
    unittest.main()
