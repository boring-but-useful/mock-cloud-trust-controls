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
            self.assertIn("## Exception Status", report)
            self.assertIn("- approved: 1", report)
            self.assertIn("- expired: 2", report)
            self.assertIn("## Active Exceptions", report)
            self.assertIn("EX-IAM-001 (MCTC-IAM-02, expires 2099-10-15)", report)
            self.assertIn("## Expired Exceptions", report)
            self.assertIn("EX-NET-001 (MCTC-NET-01, expired 2026-08-15)", report)
            self.assertIn(
                "MCTC-VULN-01: Vulnerability Findings Are Triaged And Remediated",
                report,
            )

    def test_generate_report_stops_when_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            report_path = project_copy / "reports" / "sample_report.md"
            report_path.unlink()
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
            evidence["evidence_items"][0]["status"] = "unknown"
            evidence_path.write_text(
                yaml.safe_dump(evidence, sort_keys=False),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "scripts/generate_report.py"],
                cwd=project_copy,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "Report generation stopped because validation failed:",
                result.stdout,
            )
            self.assertFalse(report_path.exists())


if __name__ == "__main__":
    unittest.main()
