#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
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
    "evidence_id",
    "control_id",
    "source_system",
    "collection_method",
    "collection_date",
    "owner",
    "status",
    "summary",
}

REQUIRED_EXCEPTION_FIELDS = {
    "exception_id",
    "control_id",
    "title",
    "owner",
    "reason",
    "compensating_control",
    "approved_by",
    "expires_on",
    "status",
}


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


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
    required_fields: set[str],
    control_ids: set[str],
    label: str,
    id_field: str,
) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be a mapping")
            continue

        missing = sorted(field for field in required_fields if field not in item)
        for field in missing:
            errors.append(f"{label}[{index}] missing required field '{field}'")

        item_id = item.get(id_field)
        if isinstance(item_id, str):
            if item_id in seen_ids:
                errors.append(f"{label}[{index}] duplicate id '{item_id}'")
            seen_ids.add(item_id)

        control_id = item.get("control_id")
        if control_id not in control_ids:
            errors.append(f"{label}[{index}] references unknown control '{control_id}'")

    return errors


def main() -> int:
    errors: list[str] = []
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

    evidence_data = load_yaml(EVIDENCE_FILE)
    evidence_items = evidence_data.get("evidence_items", []) if isinstance(evidence_data, dict) else []
    errors.extend(
        validate_reference_items(
            evidence_items,
            REQUIRED_EVIDENCE_FIELDS,
            control_ids,
            "evidence_items",
            "evidence_id",
        )
    )

    exceptions_data = load_yaml(EXCEPTIONS_FILE)
    exception_items = exceptions_data.get("exceptions", []) if isinstance(exceptions_data, dict) else []
    errors.extend(
        validate_reference_items(
            exception_items,
            REQUIRED_EXCEPTION_FIELDS,
            control_ids,
            "exceptions",
            "exception_id",
        )
    )

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(controls)} controls")
    print(f"Validated {len(evidence_items)} evidence items")
    print(f"Validated {len(exception_items)} exceptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
