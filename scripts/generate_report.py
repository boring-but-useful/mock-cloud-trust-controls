#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_DIR = PROJECT_ROOT / "controls"
EVIDENCE_FILE = PROJECT_ROOT / "examples" / "mock_evidence.yaml"
EXCEPTIONS_FILE = PROJECT_ROOT / "examples" / "mock_exceptions.yaml"
REPORT_FILE = PROJECT_ROOT / "reports" / "sample_report.md"


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_controls() -> list[dict]:
    controls = []
    for path in sorted(CONTROLS_DIR.glob("MCTC-*.yaml")):
        data = load_yaml(path)
        if isinstance(data, dict):
            controls.append(data)
    return controls


def main() -> int:
    controls = load_controls()
    evidence_data = load_yaml(EVIDENCE_FILE)
    exception_data = load_yaml(EXCEPTIONS_FILE)

    evidence_items = evidence_data.get("evidence_items", []) if isinstance(evidence_data, dict) else []
    exception_items = exception_data.get("exceptions", []) if isinstance(exception_data, dict) else []

    evidence_by_control: dict[str, list[dict]] = defaultdict(list)
    for item in evidence_items:
        evidence_by_control[item.get("control_id", "")].append(item)

    exceptions_by_control: dict[str, list[dict]] = defaultdict(list)
    for item in exception_items:
        exceptions_by_control[item.get("control_id", "")].append(item)

    status_counts = Counter(item.get("status", "unknown") for item in evidence_items)
    domain_counts = Counter(control.get("domain", "Unknown") for control in controls)

    lines = [
        "# Mock Cloud Trust Controls - Sample Report",
        "",
        "This report is generated from mock controls, evidence, and exception data. It is public-safe and illustrative only.",
        "",
        "## Summary",
        "",
        f"- Controls reviewed: {len(controls)}",
        f"- Evidence items: {len(evidence_items)}",
        f"- Exceptions: {len(exception_items)}",
        "",
        "## Evidence Status",
        "",
    ]

    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Controls By Domain", ""])
    for domain, count in sorted(domain_counts.items()):
        lines.append(f"- {domain}: {count}")

    lines.extend(["", "## Control Detail", ""])

    for control in controls:
        control_id = control["control_id"]
        lines.extend(
            [
                f"### {control_id}: {control['title']}",
                "",
                f"- Domain: {control['domain']}",
                f"- Owner: {control['owner']}",
                f"- Review cadence: {control['review_cadence']}",
                f"- Automation status: {control['automation_status']}",
                f"- Exception allowed: {control['exception_allowed']}",
                f"- Objective: {control['objective']}",
                "",
                "Evidence:",
            ]
        )

        for evidence in evidence_by_control.get(control_id, []):
            lines.append(
                f"- {evidence['evidence_id']} ({evidence['status']}): {evidence['summary']}"
            )

        if not evidence_by_control.get(control_id):
            lines.append("- No evidence sample provided.")

        lines.append("")
        lines.append("Exceptions:")
        for exception in exceptions_by_control.get(control_id, []):
            lines.append(
                f"- {exception['exception_id']} ({exception['status']}, expires {exception['expires_on']}): {exception['title']}"
            )

        if not exceptions_by_control.get(control_id):
            lines.append("- No open mock exception.")

        lines.append("")

    REPORT_FILE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_FILE.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
