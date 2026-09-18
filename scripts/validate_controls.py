#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import sys

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_DIR = PROJECT_ROOT / "controls"
EVIDENCE_FILE = PROJECT_ROOT / "examples" / "mock_evidence.yaml"
EXCEPTIONS_FILE = PROJECT_ROOT / "examples" / "mock_exceptions.yaml"

REQUIRED_CONTROL_FIELDS = {
    "control_id": str,
    "domain": str,
    "title": str,
    "objective": str,
    "requirement": str,
    "risk": str,
    "evidence_sources": list,
    "test_method": str,
    "owner": str,
    "review_cadence": str,
    "automation_status": str,
    "exception_allowed": bool,
    "exception_requirements": list,
    "related_frameworks": list,
    "tags": list,
}

REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id": str,
    "control_id": str,
    "source_system": str,
    "collection_method": str,
    "collection_date": (str, date),
    "owner": str,
    "status": str,
    "summary": str,
}

REQUIRED_EXCEPTION_FIELDS = {
    "exception_id": str,
    "control_id": str,
    "title": str,
    "owner": str,
    "reason": str,
    "compensating_control": str,
    "approved_by": str,
    "expires_on": (str, date),
    "status": str,
}

EVIDENCE_STATUSES = {"pass", "needs_review"}
EXCEPTION_STATUSES = {"approved", "expired"}
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXCEPTION_EXPIRY_WARNING_DAYS = 30


@dataclass(frozen=True)
class ValidationResult:
    counts: dict[str, int]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def expected_type_name(expected_type: type | tuple[type, ...]) -> str:
    if isinstance(expected_type, tuple):
        return " or ".join(item.__name__ for item in expected_type)
    return expected_type.__name__


def parse_iso_date(value: object) -> date | None:
    if type(value) is date:
        return value
    if not isinstance(value, str) or not ISO_DATE_PATTERN.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def validate_control(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    data = load_yaml(path)
    if not isinstance(data, dict):
        return {}, [f"{path.name}: control file must contain a YAML mapping"]

    for field, expected_type in REQUIRED_CONTROL_FIELDS.items():
        if field not in data:
            errors.append(f"{path.name}: missing required field '{field}'")
            continue
        if not isinstance(data[field], expected_type):
            errors.append(
                f"{path.name}: field '{field}' must be {expected_type.__name__}"
            )

    control_id = data.get("control_id")
    if isinstance(control_id, str) and path.stem != control_id:
        errors.append(f"{path.name}: filename must match control_id '{control_id}'")

    evidence_sources = data.get("evidence_sources", [])
    if isinstance(evidence_sources, list):
        for index, source in enumerate(evidence_sources, start=1):
            if not isinstance(source, dict):
                errors.append(f"{path.name}: evidence_sources[{index}] must be a mapping")
                continue
            for field in ("name", "system", "collection_method"):
                if not source.get(field):
                    errors.append(
                        f"{path.name}: evidence_sources[{index}] missing '{field}'"
                    )

    return data, errors


def validate_reference_items(
    items: list[dict],
    required_fields: dict[str, type | tuple[type, ...]],
    control_ids: set[str],
    label: str,
    id_field: str,
    allowed_statuses: set[str],
    date_field: str,
    as_of: date,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be a mapping")
            continue

        missing = sorted(field for field in required_fields if field not in item)
        for field in missing:
            errors.append(f"{label}[{index}] missing required field '{field}'")

        for field, expected_type in required_fields.items():
            if field in item and not isinstance(item[field], expected_type):
                errors.append(
                    f"{label}[{index}] field '{field}' must be "
                    f"{expected_type_name(expected_type)}"
                )

        item_id = item.get(id_field)
        if isinstance(item_id, str):
            if item_id in seen_ids:
                errors.append(f"{label}[{index}] duplicate id '{item_id}'")
            seen_ids.add(item_id)

        control_id = item.get("control_id")
        if control_id not in control_ids:
            errors.append(f"{label}[{index}] references unknown control '{control_id}'")

        status = item.get("status")
        if isinstance(status, str) and status not in allowed_statuses:
            allowed = ", ".join(sorted(allowed_statuses))
            errors.append(
                f"{label}[{index}] status '{status}' is not allowed; expected one of: {allowed}"
            )

        parsed_date = parse_iso_date(item.get(date_field))
        if date_field in item and parsed_date is None:
            errors.append(
                f"{label}[{index}] field '{date_field}' must be an ISO date (YYYY-MM-DD)"
            )

        if label == "exceptions" and parsed_date is not None:
            if status == "approved" and parsed_date < as_of:
                errors.append(
                    f"{label}[{index}] approved exception expired on {parsed_date.isoformat()}; "
                    "set status to 'expired'"
                )
            if status == "approved" and parsed_date >= as_of:
                days_remaining = (parsed_date - as_of).days
                if days_remaining <= EXCEPTION_EXPIRY_WARNING_DAYS:
                    timing = (
                        "today"
                        if days_remaining == 0
                        else f"in {days_remaining} days"
                    )
                    warnings.append(
                        f"{label}[{index}] approved exception expires {timing} "
                        f"on {parsed_date.isoformat()}"
                    )
            if status == "expired" and parsed_date >= as_of:
                errors.append(
                    f"{label}[{index}] expired exception has not reached its expiry date "
                    f"{parsed_date.isoformat()}"
                )

    return errors, warnings


def load_reference_items(
    path: Path,
    root_key: str,
    errors: list[str],
) -> list[dict]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        errors.append(f"{path.name}: root must be a YAML mapping")
        return []

    items = data.get(root_key)
    if not isinstance(items, list):
        errors.append(f"{path.name}: '{root_key}' must be a list")
        return []

    return items


def validate_project(as_of: date | None = None) -> ValidationResult:
    reference_date = as_of or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    controls: list[dict] = []
    control_ids: set[str] = set()

    control_paths = sorted(CONTROLS_DIR.glob("MCTC-*.yaml"))
    if not control_paths:
        errors.append("No control YAML files found")

    for path in control_paths:
        control, control_errors = validate_control(path)
        errors.extend(control_errors)
        control_id = control.get("control_id")
        if isinstance(control_id, str):
            if control_id in control_ids:
                errors.append(f"{path.name}: duplicate control_id '{control_id}'")
            control_ids.add(control_id)
        if control:
            controls.append(control)

    evidence_items = load_reference_items(EVIDENCE_FILE, "evidence_items", errors)
    evidence_errors, evidence_warnings = validate_reference_items(
        evidence_items,
        REQUIRED_EVIDENCE_FIELDS,
        control_ids,
        "evidence_items",
        "evidence_id",
        EVIDENCE_STATUSES,
        "collection_date",
        reference_date,
    )
    errors.extend(evidence_errors)
    warnings.extend(evidence_warnings)

    exception_items = load_reference_items(EXCEPTIONS_FILE, "exceptions", errors)
    exception_errors, exception_warnings = validate_reference_items(
        exception_items,
        REQUIRED_EXCEPTION_FIELDS,
        control_ids,
        "exceptions",
        "exception_id",
        EXCEPTION_STATUSES,
        "expires_on",
        reference_date,
    )
    errors.extend(exception_errors)
    warnings.extend(exception_warnings)

    counts = {
        "controls": len(controls),
        "evidence_items": len(evidence_items),
        "exceptions": len(exception_items),
    }
    return ValidationResult(counts, tuple(errors), tuple(warnings))


def main() -> int:
    result = validate_project()

    if not result.is_valid:
        print("Validation failed:")
        for error in result.errors:
            print(f"- {error}")
        return 1

    if result.warnings:
        print("Validation warnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    print(f"Validated {result.counts['controls']} controls")
    print(f"Validated {result.counts['evidence_items']} evidence items")
    print(f"Validated {result.counts['exceptions']} exceptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
