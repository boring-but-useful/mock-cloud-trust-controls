#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Callable, Sequence

from validate_controls import (
    DataLoadError,
    PROVIDERS,
    load_yaml,
    parse_date_argument,
    validate_project,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_DIR = PROJECT_ROOT / "controls"
EVIDENCE_FILE = PROJECT_ROOT / "examples" / "mock_evidence.yaml"
EXCEPTIONS_FILE = PROJECT_ROOT / "examples" / "mock_exceptions.yaml"
REPORT_FILES = {
    "markdown": PROJECT_ROOT / "reports" / "sample_report.md",
    "csv": PROJECT_ROOT / "reports" / "sample_report.csv",
    "json": PROJECT_ROOT / "reports" / "sample_report.json",
}


def load_controls() -> list[dict]:
    controls = []
    for path in sorted(CONTROLS_DIR.glob("MCTC-*.yaml")):
        data = load_yaml(path)
        if isinstance(data, dict):
            controls.append(data)
    return controls


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a report from validated project data."
    )
    parser.add_argument(
        "--as-of",
        type=parse_date_argument,
        help="Evaluate time-sensitive rules as of YYYY-MM-DD (default: today).",
    )
    parser.add_argument(
        "--format",
        choices=tuple(REPORT_FILES),
        default="markdown",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write to this path instead of the selected format's default path.",
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


def build_report_data(
    controls: list[dict],
    evidence_items: list[dict],
    exception_items: list[dict],
    warnings: list[str],
    as_of: date,
) -> dict[str, Any]:
    evidence_by_control: dict[str, list[dict]] = defaultdict(list)
    for item in evidence_items:
        evidence_by_control[item.get("control_id", "")].append(item)

    exceptions_by_control: dict[str, list[dict]] = defaultdict(list)
    for item in exception_items:
        exceptions_by_control[item.get("control_id", "")].append(item)

    control_results = []
    for control in controls:
        control_id = control["control_id"]
        control_evidence = evidence_by_control.get(control_id, [])
        expected_providers = {
            source["provider"] for source in control["evidence_sources"]
        }
        evidence_providers = {item["provider"] for item in control_evidence}
        evidence_owners = sorted({item["owner"] for item in control_evidence})
        control_results.append(
            {
                **control,
                "expected_evidence_providers": [
                    provider for provider in PROVIDERS if provider in expected_providers
                ],
                "evidence_providers": [
                    provider for provider in PROVIDERS if provider in evidence_providers
                ],
                "missing_evidence_providers": [
                    provider
                    for provider in PROVIDERS
                    if provider in expected_providers
                    and provider not in evidence_providers
                ],
                "evidence_owners": evidence_owners,
                "evidence": control_evidence,
                "exceptions": exceptions_by_control.get(control_id, []),
            }
        )

    status_counts = Counter(item["status"] for item in evidence_items)
    exception_status_counts = Counter(item["status"] for item in exception_items)
    domain_counts = Counter(control["domain"] for control in controls)
    provider_status = {
        provider: Counter(
            item["status"]
            for item in evidence_items
            if item["provider"] == provider
        )
        for provider in PROVIDERS
    }
    provider_coverage = {
        provider: {
            "total": sum(provider_status[provider].values()),
            "statuses": dict(sorted(provider_status[provider].items())),
        }
        for provider in PROVIDERS
    }
    evidence_owner_status = {
        owner: Counter(
            item["status"] for item in evidence_items if item["owner"] == owner
        )
        for owner in sorted({item["owner"] for item in evidence_items})
    }
    evidence_by_owner = {
        owner: {
            "total": sum(statuses.values()),
            "statuses": dict(sorted(statuses.items())),
        }
        for owner, statuses in evidence_owner_status.items()
    }
    coverage_gaps = [
        {
            "control_id": control["control_id"],
            "title": control["title"],
            "evidence_providers": control["evidence_providers"],
            "missing_providers": control["missing_evidence_providers"],
        }
        for control in control_results
        if control["missing_evidence_providers"]
    ]

    return {
        "report_title": "Mock Cloud Trust Controls - Sample Report",
        "as_of": as_of,
        "disclaimer": (
            "This report is generated from mock controls, evidence, and exception "
            "data. It is public-safe and illustrative only."
        ),
        "summary": {
            "controls_reviewed": len(controls),
            "evidence_items": len(evidence_items),
            "exceptions": len(exception_items),
        },
        "review_warnings": warnings,
        "evidence_status": dict(sorted(status_counts.items())),
        "exception_status": dict(sorted(exception_status_counts.items())),
        "active_exceptions": [
            item for item in exception_items if item["status"] == "approved"
        ],
        "expired_exceptions": [
            item for item in exception_items if item["status"] == "expired"
        ],
        "controls_by_domain": dict(sorted(domain_counts.items())),
        "evidence_by_provider": provider_coverage,
        "evidence_by_owner": evidence_by_owner,
        "provider_coverage_gaps": coverage_gaps,
        "controls": control_results,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# {report['report_title']}",
        "",
        report["disclaimer"],
        "",
        "## Summary",
        "",
        f"- Review date: {report['as_of']}",
        f"- Controls reviewed: {summary['controls_reviewed']}",
        f"- Evidence items: {summary['evidence_items']}",
        f"- Exceptions: {summary['exceptions']}",
        "",
        "## Review Warnings",
        "",
    ]

    # Keep warnings visible without blocking valid output.
    for warning in report["review_warnings"]:
        lines.append(f"- {warning}")
    if not report["review_warnings"]:
        lines.append("- No validation warnings.")

    lines.extend(["", "## Evidence Status", ""])
    for status, count in report["evidence_status"].items():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Exception Status", ""])
    for status, count in report["exception_status"].items():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Active Exceptions", ""])
    for exception in report["active_exceptions"]:
        lines.append(
            f"- {exception['exception_id']} ({exception['control_id']}, expires "
            f"{exception['expires_on']}): {exception['title']}"
        )
    if not report["active_exceptions"]:
        lines.append("- No active exceptions.")

    lines.extend(["", "## Expired Exceptions", ""])
    for exception in report["expired_exceptions"]:
        lines.append(
            f"- {exception['exception_id']} ({exception['control_id']}, expired "
            f"{exception['expires_on']}): {exception['title']}"
        )
    if not report["expired_exceptions"]:
        lines.append("- No expired exceptions.")

    lines.extend(["", "## Controls By Domain", ""])
    for domain, count in report["controls_by_domain"].items():
        lines.append(f"- {domain}: {count}")

    lines.extend(["", "## Evidence By Provider", ""])
    for provider, coverage in report["evidence_by_provider"].items():
        status_summary = ", ".join(
            f"{status}: {count}"
            for status, count in coverage["statuses"].items()
        )
        detail = f" ({status_summary})" if status_summary else ""
        lines.append(f"- {provider}: {coverage['total']}{detail}")

    lines.extend(["", "## Provider Coverage Gaps", ""])
    for gap in report["provider_coverage_gaps"]:
        present = ", ".join(gap["evidence_providers"]) or "none"
        missing = ", ".join(gap["missing_providers"])
        lines.append(
            f"- {gap['control_id']}: missing {missing}; current evidence: {present}"
        )
    if not report["provider_coverage_gaps"]:
        lines.append("- No provider coverage gaps.")

    lines.extend(["", "## Evidence By Owner", ""])
    for owner, coverage in report["evidence_by_owner"].items():
        status_summary = ", ".join(
            f"{status}: {count}"
            for status, count in coverage["statuses"].items()
        )
        lines.append(f"- {owner}: {coverage['total']} ({status_summary})")

    lines.extend(["", "## Control Detail", ""])
    for control in report["controls"]:
        lines.extend(
            [
                f"### {control['control_id']}: {control['title']}",
                "",
                f"- Domain: {control['domain']}",
                f"- Owner: {control['owner']}",
                f"- Review cadence: {control['review_cadence']}",
                f"- Automation status: {control['automation_status']}",
                f"- Exception allowed: {control['exception_allowed']}",
                f"- Objective: {control['objective']}",
                "- Expected evidence providers: "
                + ", ".join(control["expected_evidence_providers"]),
                "- Current evidence providers: "
                + (", ".join(control["evidence_providers"]) or "none"),
                "- Missing evidence providers: "
                + (", ".join(control["missing_evidence_providers"]) or "none"),
                "- Evidence owners: "
                + (", ".join(control["evidence_owners"]) or "none"),
                "",
                "Evidence:",
            ]
        )

        for evidence in control["evidence"]:
            lines.append(
                f"- {evidence['evidence_id']} "
                f"[{evidence['provider']}; {evidence['environment']}; "
                f"{evidence['scope']}] ({evidence['status']}): "
                f"{evidence['summary']}"
            )
        if not control["evidence"]:
            lines.append("- No evidence sample provided.")

        lines.extend(["", "Exceptions:"])
        for exception in control["exceptions"]:
            lines.append(
                f"- {exception['exception_id']} ({exception['status']}, "
                f"expires {exception['expires_on']}): {exception['title']}"
            )
        if not control["exceptions"]:
            lines.append("- No open mock exception.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_csv(report: dict[str, Any]) -> str:
    """Render a flat, spreadsheet-friendly control summary."""
    output = io.StringIO(newline="")
    fieldnames = [
        "as_of",
        "control_id",
        "title",
        "domain",
        "owner",
        "review_cadence",
        "automation_status",
        "exception_allowed",
        "objective",
        "evidence_count",
        "expected_evidence_providers",
        "evidence_providers",
        "missing_evidence_providers",
        "evidence_owners",
        "evidence",
        "exception_count",
        "exceptions",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()

    for control in report["controls"]:
        evidence = "; ".join(
            f"{item['evidence_id']} [{item['provider']}] ({item['status']})"
            for item in control["evidence"]
        )
        exceptions = "; ".join(
            f"{item['exception_id']} ({item['status']}, expires {item['expires_on']})"
            for item in control["exceptions"]
        )
        writer.writerow(
            {
                "as_of": report["as_of"],
                "control_id": control["control_id"],
                "title": control["title"],
                "domain": control["domain"],
                "owner": control["owner"],
                "review_cadence": control["review_cadence"],
                "automation_status": control["automation_status"],
                "exception_allowed": str(control["exception_allowed"]).lower(),
                "objective": control["objective"],
                "evidence_count": len(control["evidence"]),
                "expected_evidence_providers": "; ".join(
                    control["expected_evidence_providers"]
                ),
                "evidence_providers": "; ".join(control["evidence_providers"]),
                "missing_evidence_providers": "; ".join(
                    control["missing_evidence_providers"]
                ),
                "evidence_owners": "; ".join(control["evidence_owners"]),
                "evidence": evidence,
                "exception_count": len(control["exceptions"]),
                "exceptions": exceptions,
            }
        )

    return output.getvalue()


def normalize_json_value(value: Any) -> Any:
    # PyYAML decodes unquoted ISO dates; convert them at the serialization boundary.
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: normalize_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_json_value(item) for item in value]
    return value


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(normalize_json_value(report), indent=2, sort_keys=True) + "\n"


REPORT_RENDERERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "markdown": render_markdown,
    "csv": render_csv,
    "json": render_json,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    report_file = args.output.resolve() if args.output else REPORT_FILES[args.format]
    reference_date = args.as_of or date.today()

    # Refuse to publish reports from invalid source data.
    validation = validate_project(reference_date)
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

    report = build_report_data(
        controls,
        evidence_items,
        exception_items,
        validation.warnings,
        reference_date,
    )
    content = REPORT_RENDERERS[args.format](report)
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
