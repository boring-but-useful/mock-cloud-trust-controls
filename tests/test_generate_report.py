from __future__ import annotations

import csv
import json
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


def run_generator(
    project_root: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/generate_report.py", *arguments],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )


class GenerateReportTests(unittest.TestCase):
    def test_generate_report_writes_expected_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            report_path = project_copy / "reports" / "sample_report.md"
            report_path.unlink()

            result = run_generator(project_copy, "--as-of", "2026-09-18")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "Wrote reports/sample_report.md")
            self.assertTrue(report_path.exists())

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("# Mock Cloud Trust Controls - Sample Report", report)
            self.assertIn("- Review date: 2026-09-18", report)
            self.assertIn("- Controls reviewed: 7", report)
            self.assertIn("- Evidence items: 7", report)
            self.assertIn("- Exceptions: 3", report)
            self.assertIn("## Review Warnings", report)
            self.assertIn("- No validation warnings.", report)
            self.assertIn("## Exception Status", report)
            self.assertIn("- approved: 1", report)
            self.assertIn("- expired: 2", report)
            self.assertIn("## Active Exceptions", report)
            self.assertIn("EX-IAM-001 (MCTC-IAM-02, expires 2027-09-18)", report)
            self.assertIn("## Expired Exceptions", report)
            self.assertIn("EX-NET-001 (MCTC-NET-01, expired 2026-08-15)", report)
            self.assertIn("## Evidence By Provider", report)
            self.assertIn("- aws: 4 (needs_review: 2, pass: 2)", report)
            self.assertIn("- gcp: 0", report)
            self.assertIn("## Provider Coverage Gaps", report)
            self.assertIn(
                "MCTC-LOG-01: missing gcp, common; current evidence: aws",
                report,
            )
            self.assertIn("## Evidence By Owner", report)
            self.assertIn("- Security / IT: 1 (needs_review: 1)", report)
            self.assertIn(
                "MCTC-VULN-01: Vulnerability Findings Are Triaged And Remediated",
                report,
            )

    def test_generate_report_stops_when_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            report_path = project_copy / "reports" / "sample_report.md"
            report_path.write_text("existing valid report\n", encoding="utf-8")
            evidence_path = project_copy / "examples" / "mock_evidence.yaml"
            evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
            evidence["evidence_items"][0]["status"] = "unknown"
            evidence_path.write_text(
                yaml.safe_dump(evidence, sort_keys=False),
                encoding="utf-8",
            )

            result = run_generator(project_copy)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "Report generation stopped because validation failed:",
                result.stdout,
            )
            self.assertEqual(
                report_path.read_text(encoding="utf-8"),
                "existing valid report\n",
            )

    def test_generate_report_includes_non_blocking_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            exceptions_path = project_copy / "examples" / "mock_exceptions.yaml"
            exceptions = yaml.safe_load(exceptions_path.read_text(encoding="utf-8"))
            expires_on = date.today() + timedelta(days=10)
            exceptions["exceptions"][0]["expires_on"] = expires_on.isoformat()
            exceptions_path.write_text(
                yaml.safe_dump(exceptions, sort_keys=False),
                encoding="utf-8",
            )

            result = run_generator(project_copy)

            self.assertEqual(result.returncode, 0)
            report = (project_copy / "reports" / "sample_report.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Review Warnings", report)
            self.assertIn(
                f"approved exception expires in 10 days on {expires_on.isoformat()}",
                report,
            )

    def test_generate_report_supports_custom_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            output_path = project_copy / "build" / "review" / "report.md"

            result = run_generator(
                project_copy,
                "--output",
                str(output_path),
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "Wrote build/review/report.md")
            self.assertTrue(output_path.exists())

    def test_generate_report_writes_control_summary_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            report_path = project_copy / "reports" / "sample_report.csv"
            report_path.unlink(missing_ok=True)

            result = run_generator(
                project_copy,
                "--as-of",
                "2026-09-18",
                "--format",
                "csv",
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "Wrote reports/sample_report.csv")
            with report_path.open(encoding="utf-8", newline="") as report_file:
                rows = list(csv.DictReader(report_file))

            self.assertEqual(len(rows), 7)
            iam_control = next(
                row for row in rows if row["control_id"] == "MCTC-IAM-02"
            )
            self.assertEqual(iam_control["evidence_count"], "1")
            self.assertEqual(iam_control["evidence_providers"], "common")
            self.assertEqual(iam_control["missing_evidence_providers"], "aws")
            self.assertEqual(iam_control["evidence_owners"], "Security / IT")
            self.assertEqual(
                iam_control["evidence"],
                "EV-IAM-002 [common] (needs_review)",
            )
            self.assertEqual(iam_control["exception_count"], "1")
            self.assertIn("EX-IAM-001 (approved", iam_control["exceptions"])

    def test_generate_report_writes_complete_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            report_path = project_copy / "reports" / "sample_report.json"
            report_path.unlink(missing_ok=True)

            result = run_generator(
                project_copy,
                "--as-of",
                "2026-09-18",
                "--format",
                "json",
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "Wrote reports/sample_report.json")
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["controls_reviewed"], 7)
            self.assertEqual(report["summary"]["evidence_items"], 7)
            self.assertEqual(report["summary"]["exceptions"], 3)
            self.assertEqual(report["as_of"], "2026-09-18")
            self.assertEqual(report["review_warnings"], [])
            self.assertEqual(report["evidence_by_provider"]["aws"]["total"], 4)
            self.assertEqual(report["evidence_by_provider"]["gcp"]["total"], 0)
            self.assertEqual(report["evidence_by_owner"]["Security / IT"]["total"], 1)

            iam_control = next(
                control
                for control in report["controls"]
                if control["control_id"] == "MCTC-IAM-02"
            )
            self.assertEqual(iam_control["evidence"][0]["evidence_id"], "EV-IAM-002")
            self.assertEqual(iam_control["evidence"][0]["provider"], "common")
            self.assertEqual(iam_control["evidence_providers"], ["common"])
            self.assertEqual(iam_control["missing_evidence_providers"], ["aws"])
            self.assertEqual(
                iam_control["exceptions"][0]["expires_on"],
                "2027-09-18",
            )

    def test_generate_report_strict_warnings_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_copy = copy_project(Path(tmp_dir))
            output_path = project_copy / "build" / "strict-report.md"

            result = run_generator(
                project_copy,
                "--as-of",
                "2027-09-01",
                "--strict-warnings",
                "--output",
                str(output_path),
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("--strict-warnings was set", result.stdout)
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
