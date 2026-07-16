# Mock Cloud Trust Controls Code Walkthrough

## Big Picture

This project is a small control-framework prototype. It has three layers:

1. Structured control definitions in YAML.
2. Mock evidence and exceptions linked back to those controls.
3. Python scripts that validate the data and generate a Markdown report.

The intended flow is:

```text
control intent -> requirement -> evidence -> test -> exception -> report
```

The project is public-safe. It uses synthetic controls, synthetic evidence, and generic framework labels. It does not use employer data, production cloud data, screenshots, exports, secrets, or exact framework mappings.

## Repository Layout

```text
mock_cloud_trust_controls/
├── README.md
├── SPEC.md
├── CODE_WALKTHROUGH.md
├── requirements.txt
├── catalog.md
├── controls/
│   ├── MCTC-EVD-01.yaml
│   ├── MCTC-IAC-01.yaml
│   ├── MCTC-IAM-01.yaml
│   ├── MCTC-IAM-02.yaml
│   ├── MCTC-LOG-01.yaml
│   ├── MCTC-NET-01.yaml
│   └── MCTC-VULN-01.yaml
├── examples/
│   ├── mock_evidence.yaml
│   └── mock_exceptions.yaml
├── reports/
│   └── sample_report.md
├── scripts/
│   ├── generate_report.py
│   └── validate_controls.py
└── tests/
    ├── test_generate_report.py
    └── test_validate_controls.py
```

## Control Files

The control definitions live in `controls/*.yaml`.

Each control is one YAML mapping. The filename must match the `control_id`. For example:

```text
controls/MCTC-VULN-01.yaml
```

contains:

```yaml
control_id: MCTC-VULN-01
domain: Vulnerability and configuration management
title: Vulnerability Findings Are Triaged And Remediated
```

Each control describes:

- what risk the control reduces
- what the organization requires
- what evidence should prove it is operating
- how a reviewer can test it
- who owns it
- how often it is reviewed
- whether exceptions are allowed
- what an exception must include

Current controls:

| Control ID | Domain | Purpose |
|---|---|---|
| MCTC-IAM-01 | Identity and access | Restrict privileged access to approved users and roles. |
| MCTC-IAM-02 | Identity and access | Require central authentication for human access. |
| MCTC-LOG-01 | Logging and monitoring | Ensure cloud audit logs are enabled and retained. |
| MCTC-IAC-01 | Infrastructure as code | Ensure infrastructure changes are reviewed and versioned. |
| MCTC-NET-01 | Cloud network exposure | Ensure internet exposure is approved and documented. |
| MCTC-EVD-01 | Incident response and evidence handling | Ensure evidence is source-linked and repeatable. |
| MCTC-VULN-01 | Vulnerability and configuration management | Ensure findings are triaged, owned, remediated, or excepted. |

## Mock Evidence

Evidence lives in:

```text
examples/mock_evidence.yaml
```

The file has a root key named `evidence_items`.

Each evidence item has:

- `evidence_id`
- `control_id`
- `source_system`
- `collection_method`
- `collection_date`
- `owner`
- `status`
- `summary`

The important link is `control_id`. That is how evidence gets attached to a control in the generated report.

Example:

```yaml
- evidence_id: EV-VULN-001
  control_id: MCTC-VULN-01
  source_system: AWS Security Hub
  status: needs_review
```

Current evidence statuses:

- `pass`
- `needs_review`

## Mock Exceptions

Exceptions live in:

```text
examples/mock_exceptions.yaml
```

The file has a root key named `exceptions`.

Each exception has:

- `exception_id`
- `control_id`
- `title`
- `owner`
- `reason`
- `compensating_control`
- `approved_by`
- `expires_on`
- `status`

The important link is also `control_id`. Exceptions are grouped under the relevant control in the generated report.

Current exceptions are all synthetic and approved. They cover break-glass access, temporary public exposure, and a dependency finding awaiting an upstream patch.

## Validator

The validator is:

```text
scripts/validate_controls.py
```

Run it from the project root:

```bash
python3 scripts/validate_controls.py
```

Expected output:

```text
Validated 7 controls
Validated 7 evidence items
Validated 3 exceptions
```

### What It Checks

The script starts by locating the project root relative to itself:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTROLS_DIR = PROJECT_ROOT / "controls"
EVIDENCE_FILE = PROJECT_ROOT / "examples" / "mock_evidence.yaml"
EXCEPTIONS_FILE = PROJECT_ROOT / "examples" / "mock_exceptions.yaml"
```

This means the script can be run from the repo layout without hard-coded absolute paths.

It then defines required fields for:

- controls
- evidence items
- exception items

For controls, it validates:

- the YAML file is a mapping
- required fields exist
- required fields have the expected Python type
- `control_id` matches the filename
- each `evidence_sources` entry includes `name`, `system`, and `collection_method`
- duplicate control IDs are rejected

For evidence and exceptions, it validates:

- required fields exist
- IDs are not duplicated
- each item references a known `control_id`

If anything fails, the validator prints every error and returns exit code `1`. If everything passes, it prints the counts and returns `0`.

## Report Generator

The report generator is:

```text
scripts/generate_report.py
```

Run it from the project root:

```bash
python3 scripts/generate_report.py
```

Expected output:

```text
Wrote reports/sample_report.md
```

### What It Does

The generator loads:

- all controls from `controls/MCTC-*.yaml`
- mock evidence from `examples/mock_evidence.yaml`
- mock exceptions from `examples/mock_exceptions.yaml`

It groups evidence and exceptions by `control_id`:

```python
evidence_by_control[item.get("control_id", "")].append(item)
exceptions_by_control[item.get("control_id", "")].append(item)
```

It also calculates:

- evidence status counts
- control counts by domain

Then it builds a Markdown report as a list of strings and writes:

```text
reports/sample_report.md
```

The report includes:

- total controls reviewed
- total evidence items
- total exceptions
- evidence status summary
- controls by domain
- per-control detail
- linked evidence summaries
- linked exception summaries

## Generated Report

The current generated report is:

```text
reports/sample_report.md
```

Current summary:

```text
Controls reviewed: 7
Evidence items: 7
Exceptions: 3
```

Current evidence status counts:

```text
pass: 4
needs_review: 3
```

The report is generated output, but it is intentionally committed for now because it shows what the tool produces without requiring someone to run the script first.

## Current Design Choices

- YAML is used because the controls should be readable as documents and parseable as data.
- The schema is deliberately simple so the project can grow without a database or API.
- The validator is strict enough to catch broken references and missing fields.
- The report generator assumes validation has already passed.
- The unittest coverage exercises the command-line scripts against a temporary copy of the project, which keeps tests close to real usage.
- Framework labels are generic, such as `SOC 2 style` and `ISO 27001 style`, until official mappings are verified.

## Known Limitations

- The report generator does not call the validator before generating output.
- Evidence statuses are not constrained to an enum yet.
- Exception dates are not checked for expiry yet.
- There is no CSV output yet.
- There are no real cloud integrations yet.
- There is no separate development requirements file yet.

## Near-Term Next Steps

Good next engineering slices:

1. Add CSV report output.
2. Add richer mock AWS Config, Security Hub, IAM, CloudTrail, and Terraform evidence.
3. Add finding severity, finding age, owner, and due-date fields.
4. Add rollups by domain, owner, status, and exception expiry.
5. Add more negative validation tests as the schema becomes stricter.
6. Verify exact framework mappings from primary sources before adding official mappings.
