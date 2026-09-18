# Mock Cloud Trust Controls Specification

## Purpose

Mock Cloud Trust Controls is a small, public-safe control framework for practicing trust, security, compliance, and evidence automation work.

The project demonstrates how to move from control intent to reviewable evidence:

```text
control intent -> requirement -> evidence -> test -> exception -> report
```

It does not copy employer control language, use production data, or claim official SOC 2, ISO, CIS, or NIST coverage.

## Current Version

Current project state:

- 7 YAML control definitions
- 7 mock evidence records
- 3 mock exception records
- Markdown control catalog
- Readable code walkthrough
- Requirements file for local setup
- Python validation script
- Python Markdown report generator
- Unittest coverage for validation and report generation
- Generated sample report
- Local git repository with `main` as the stable default branch
- GitHub remote configured as `origin`

## Goals

- Write clear, testable security controls.
- Map controls to concrete evidence sources.
- Model control exceptions with owners, reasons, expiry dates, and compensating controls.
- Validate control and evidence files locally.
- Generate a reviewable evidence report from structured data.
- Keep all examples public-safe and synthetic.

## Non-Goals

- No official framework mappings until verified from primary sources.
- No real employer, customer, account, asset, or vulnerability data.
- No cloud API calls in the current version.
- No secrets, credentials, or GitHub tokens in the repository.
- No claim that the sample report represents an actual audit result.

## Project Structure

```text
mock_cloud_trust_controls/
├── README.md
├── SPEC.md
├── CODE_WALKTHROUGH.md
├── ROADMAP.md
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

## Control Catalog

| Control ID | Domain | Title | Review Cadence | Automation Status |
|---|---|---|---|---|
| MCTC-IAM-01 | Identity and access | Privileged Access Is Restricted | Quarterly | Partial |
| MCTC-IAM-02 | Identity and access | Human Access Uses Central Authentication | Quarterly | Partial |
| MCTC-LOG-01 | Logging and monitoring | Cloud Audit Logs Are Enabled And Retained | Monthly | Partial |
| MCTC-IAC-01 | Infrastructure as code | Infrastructure Changes Are Reviewed And Versioned | Monthly | Manual sample |
| MCTC-NET-01 | Cloud network exposure | Internet Exposure Is Approved And Documented | Monthly | Partial |
| MCTC-EVD-01 | Incident response and evidence handling | Evidence Is Source-Linked And Repeatable | Quarterly | Manual sample |
| MCTC-VULN-01 | Vulnerability and configuration management | Vulnerability Findings Are Triaged And Remediated | Monthly | Partial |

## Control Schema

Each control file is a YAML mapping named after its control ID:

```text
controls/MCTC-AREA-##.yaml
```

Required fields:

- `control_id`: Unique control identifier. Must match the file stem.
- `domain`: Control domain.
- `title`: Human-readable control title.
- `objective`: One-sentence control intent.
- `requirement`: Testable requirement.
- `risk`: Risk reduced by the control.
- `evidence_sources`: List of evidence source mappings.
- `test_method`: How a reviewer can test the control.
- `owner`: Responsible team or role.
- `review_cadence`: Review frequency.
- `automation_status`: Current automation maturity.
- `exception_allowed`: Boolean.
- `exception_requirements`: Required fields or conditions for exceptions.
- `related_frameworks`: Illustrative framework labels only.
- `tags`: Search and grouping tags.

Each `evidence_sources` item requires:

- `name`
- `system`
- `collection_method`

## Evidence Schema

Mock evidence lives in:

```text
examples/mock_evidence.yaml
```

The root key is `evidence_items`.

Each evidence item requires:

- `evidence_id`
- `control_id`
- `source_system`
- `collection_method`
- `collection_date`
- `owner`
- `status`
- `summary`

Current evidence statuses:

- `pass`
- `needs_review`

## Exception Schema

Mock exceptions live in:

```text
examples/mock_exceptions.yaml
```

The root key is `exceptions`.

Each exception requires:

- `exception_id`
- `control_id`
- `title`
- `owner`
- `reason`
- `compensating_control`
- `approved_by`
- `expires_on`
- `status`

Current exception statuses:

- `approved`
- `expired`

## Validation

Run from the project root:

```bash
python3 scripts/validate_controls.py
```

The validator checks:

- control YAML files exist
- required control fields are present
- required field types are correct
- control filenames match `control_id`
- evidence source entries include name, system, and collection method
- duplicate control IDs are rejected
- evidence and exception required field types are correct
- evidence and exception statuses use documented values
- evidence collection dates and exception expiry dates use ISO `YYYY-MM-DD` format
- approved exceptions have not passed their expiry dates
- evidence records reference known controls
- exception records reference known controls
- evidence and exception IDs are duplicate-checked

Current expected output:

```text
Validated 7 controls
Validated 7 evidence items
Validated 3 exceptions
```

## Report Generation

Run from the project root:

```bash
python3 scripts/generate_report.py
```

The generator reads:

- `controls/*.yaml`
- `examples/mock_evidence.yaml`
- `examples/mock_exceptions.yaml`

It writes:

```text
reports/sample_report.md
```

The report includes:

- total controls reviewed
- total evidence items
- total exceptions
- evidence status counts
- exception status counts
- active exception summary
- expired exception summary
- controls by domain
- per-control details
- linked evidence summaries
- linked exception summaries

## Dependencies

Runtime:

- Python 3
- PyYAML

Install dependencies from:

```bash
python3 -m pip install -r requirements.txt
```

## Tests

Run from the project root:

```bash
python3 -m unittest discover -s tests
```

The tests copy the project into a temporary directory, run the command-line scripts against that copy, and verify:

- validation passes for the current project data
- validation reports a missing required control field
- report generation writes the expected Markdown output

## Public-Safe Rules

- Use mock account IDs and mock resources only.
- Do not add employer control text.
- Do not add screenshots or exports from real systems.
- Do not claim exact framework mapping until verified.
- Keep framework references generic until mappings are checked.
- Keep examples focused on judgment, evidence quality, and repeatable workflow.

## Git / Publishing State

The project is initialized as a local git repository under:

```text
Job_Search_2026/Portfolio/mock_cloud_trust_controls
```

Current branch:

```text
main
```

Default GitHub branch:

```text
main
```

Remote:

```text
origin https://github.com/boring-but-useful/mock-cloud-trust-controls.git
```

Branch policy:

- Treat `main` as the default and stable branch.
- Do not make direct feature changes on `main`.
- Open pull requests from short-lived branches for documentation, control, data, or script changes.
- Keep generated report updates in the same pull request as the data or generator change that produced them.

Normal change flow:

```bash
git switch -c short-description
python3 scripts/validate_controls.py
python3 scripts/generate_report.py
git push -u origin short-description
```

## Near-Term Roadmap

See [ROADMAP.md](ROADMAP.md) for the staged implementation plan and completion criteria.
