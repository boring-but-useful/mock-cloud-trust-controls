#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence

from validate_controls import (
    DataLoadError,
    load_yaml,
    parse_date_argument,
    validate_project,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_DIR = PROJECT_ROOT / "controls"
EVIDENCE_FILE = PROJECT_ROOT / "examples" / "mock_evidence.yaml"
EXCEPTIONS_FILE = PROJECT_ROOT / "examples" / "mock_exceptions.yaml"
REPORT_FILE = PROJECT_ROOT / "reports" / "sample_report.md"


def load_controls() -> list[dict]:
    controls = []
    for path in sorted(CONTROLS_DIR.glob("MCTC-*.yaml")):
        data = load_yaml(path)
        if isinstance(data, dict):
            controls.append(data)
    return controls


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown report from validated project data."
    )
    parser.add_argument(
        "--as-of",
        type=parse_date_argument,
        help="Evaluate time-sensitive rules as of YYYY-MM-DD (default: today).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write to this path instead of reports/sample_report.md.",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Do not write a report when otherwise valid data has warnings.",
    )
    return parser


def write_text_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except OSError:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def display_path(path: Path) -> Path:
    try:
        return path.relative_to(PROJECT_ROOT)
    except ValueError:
        return path


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    report_file = args.output.resolve() if args.output else REPORT_FILE

    # Refuse to publish reports from invalid source data.
    validation = validate_project(args.as_of)
    if not validation.is_valid:
        print("Report generation stopped because validation failed:")
        for error in validation.errors:
            print(f"- {error}")
        return 1
    if args.strict_warnings and validation.warnings:
        print("Report generation stopped because --strict-warnings was set:")
        for warning in validation.warnings:
            print(f"- {warning}")
        return 1

    try:
        controls = load_controls()
        evidence_data = load_yaml(EVIDENCE_FILE)
        exception_data = load_yaml(EXCEPTIONS_FILE)
    except DataLoadError as error:
        print(f"Report generation stopped: {error}")
        return 1

    evidence_items = (
        evidence_data.get("evidence_items", [])
        if isinstance(evidence_data, dict)
        else []
    )
    exception_items = (
        exception_data.get("exceptions", [])
        if isinstance(exception_data, dict)
        else []
    )

    evidence_by_control: dict[str, list[dict]] = defaultdict(list)
    for item in evidence_items:
        evidence_by_control[item.get("control_id", "")].append(item)

    exceptions_by_control: dict[str, list[dict]] = defaultdict(list)
    for item in exception_items:
        exceptions_by_control[item.get("control_id", "")].append(item)

    status_counts = Counter(item.get("status", "unknown") for item in evidence_items)
    exception_status_counts = Counter(
        item.get("status", "unknown") for item in exception_items
    )
    domain_counts = Counter(control.get("domain", "Unknown") for control in controls)

    lines = [
        "# Mock Cloud Trust Controls - Sample Report",
        "",
        "This report is generated from mock controls, evidence, and exception "
        "data. It is public-safe and illustrative only.",
        "",
        "## Summary",
        "",
        f"- Controls reviewed: {len(controls)}",
        f"- Evidence items: {len(evidence_items)}",
        f"- Exceptions: {len(exception_items)}",
        "",
        "## Review Warnings",
        "",
    ]

    # Keep warnings visible without blocking valid output.
    for warning in validation.warnings:
        lines.append(f"- {warning}")
    if not validation.warnings:
        lines.append("- No validation warnings.")

    lines.extend(
        [
            "",
            "## Evidence Status",
            "",
        ]
    )

    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Exception Status", ""])
    for status, count in sorted(exception_status_counts.items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Active Exceptions", ""])
    active_exceptions = [
        item for item in exception_items if item.get("status") == "approved"
    ]
    for exception in active_exceptions:
        lines.append(
            f"- {exception['exception_id']} ({exception['control_id']}, expires "
            f"{exception['expires_on']}): {exception['title']}"
        )
    if not active_exceptions:
        lines.append("- No active exceptions.")

    lines.extend(["", "## Expired Exceptions", ""])
    expired_exceptions = [
        item for item in exception_items if item.get("status") == "expired"
    ]
    for exception in expired_exceptions:
        lines.append(
            f"- {exception['exception_id']} ({exception['control_id']}, expired "
            f"{exception['expires_on']}): {exception['title']}"
        )
    if not expired_exceptions:
        lines.append("- No expired exceptions.")

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
                f"- {exception['exception_id']} ({exception['status']}, "
                f"expires {exception['expires_on']}): {exception['title']}"
            )

        if not exceptions_by_control.get(control_id):
            lines.append("- No open mock exception.")

        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    try:
        write_text_atomically(report_file, content)
    except OSError as error:
        detail = error.strerror or error.__class__.__name__
        print(f"Report generation stopped: unable to write report ({detail})")
        return 1

    print(f"Wrote {display_path(report_file)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
