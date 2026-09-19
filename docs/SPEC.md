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

- 10 YAML control definitions
- 17 mock evidence records
- 4 mock exception records
- Markdown control catalog
- Readable code walkthrough
- Requirements file for local setup
- Python validation script
- Python Markdown, CSV, and JSON report generator
- Provider-aware evidence records and coverage-gap reporting
- Unittest coverage for validation, documentation links, and report generation
- Command-line support for reproducible review dates, strict warnings, and custom report paths
- Controlled YAML and file-loading errors
- Atomic report writes
- One-command local verification through `make verify`
- GitHub Actions verification and weekly Dependabot checks
- Generated Markdown, CSV, and JSON sample reports
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
├── .github/
│   ├── dependabot.yml
│   └── workflows/verify.yml
├── .python-version
├── AGENTS.md
├── README.md
├── ROADMAP.md
├── SECURITY.md
├── Makefile
├── requirements.txt
├── catalog.md
├── docs/
│   ├── assets/
│   │   ├── cloud_logging_architecture.mmd
│   │   └── cloud_logging_architecture.svg
│   ├── CLOUD_LOGGING_ARCHITECTURE.md
│   ├── CODE_WALKTHROUGH.md
│   ├── DESIGN_PRINCIPLES.md
│   ├── FINOPS_CONTROL_GUIDE.md
│   ├── PROVIDER_EVIDENCE_MODEL.md
│   └── SPEC.md
├── controls/
│   ├── MCTC-EVD-01.yaml
│   ├── MCTC-COST-01.yaml
│   ├── MCTC-COST-02.yaml
│   ├── MCTC-COST-03.yaml
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
│   ├── sample_report.csv
│   ├── sample_report.json
│   └── sample_report.md
├── scripts/
│   ├── check_markdown_links.py
│   ├── generate_report.py
│   └── validate_controls.py
└── tests/
    ├── test_check_markdown_links.py
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
| MCTC-COST-01 | FinOps and cost governance | Cloud Spend Is Allocated And Owned | Monthly | Partial |
| MCTC-COST-02 | FinOps and cost governance | Budgets Forecasts And Cost Anomalies Are Reviewed | Monthly | Partial |
| MCTC-COST-03 | FinOps and cost governance | Cost Optimization Decisions Protect Reliability | Monthly | Partial |

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
- `provider`: `aws`, `gcp`, or `common`
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
- `provider`: `aws`, `gcp`, or `common`
- `scope`: synthetic account, organization, folder, project, or shared-system reference
- `environment`: `production`, `staging`, or `shared`
- `source_system`
- `collection_method`
- `collection_date`
- `owner`
- `status`
- `summary`

`resource_ref` is optional. When present, it must be a non-empty synthetic reference.

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
- evidence source entries include name, provider, system, and collection method
- evidence sources and evidence records use an allowed provider
- evidence records include a non-empty scope and allowed environment
- optional resource references are non-empty strings
- duplicate control IDs are rejected
- evidence and exception required field types are correct
- evidence and exception statuses use documented values
- evidence collection dates and exception expiry dates use ISO `YYYY-MM-DD` format
- approved exceptions have not passed their expiry dates
- approved exceptions expiring within 30 days produce a non-blocking review warning
- invalid YAML and unreadable required files produce controlled validation errors
- evidence records reference known controls
- exception records reference known controls
- evidence and exception IDs are duplicate-checked

Current expected output:

```text
Validated 10 controls
Validated 17 evidence items
Validated 4 exceptions
```

Local Markdown links are checked separately with:

```bash
python3 scripts/check_markdown_links.py
```

The check rejects missing inline document or image targets and local paths that escape the repository. External URLs and same-page fragments are not resolved.

## Report Generation

Run from the project root:

```bash
python3 scripts/generate_report.py
python3 scripts/generate_report.py --format csv
python3 scripts/generate_report.py --format json
```

The generator reads:

- `controls/*.yaml`
- `examples/mock_evidence.yaml`
- `examples/mock_exceptions.yaml`

The format selects the default output path:

```text
markdown -> reports/sample_report.md
csv      -> reports/sample_report.csv
json     -> reports/sample_report.json
```

Markdown is the default. CSV is a flat, one-row-per-control summary designed for spreadsheets. JSON preserves the full nested report data for downstream automation. The output path can be changed with `--output`; `--format` remains authoritative when a custom path is used. Report writes use a temporary file in the destination directory followed by an atomic replacement so failed writes do not truncate the last valid report.

The effective `--as-of` date is recorded in every format. The committed sample artifacts use the `Makefile`'s fixed `SAMPLE_AS_OF` value so they remain deterministic while standalone CLI runs continue to default to the current date.

The report includes:

- total controls reviewed
- total evidence items
- total exceptions
- validation warnings
- evidence status counts
- exception status counts
- active exception summary
- expired exception summary
- controls by domain
- per-control details
- linked evidence summaries
- linked exception summaries
- evidence totals and statuses by provider
- evidence totals and statuses by owner
- expected, present, and missing evidence providers by control

## Dependencies

Runtime:

- Python 3.12
- PyYAML 6.0.3

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

- local Markdown links accept valid files and reject missing or escaping targets
- validation passes for the current project data
- validation reports a missing required control field
- report generation writes the expected Markdown output
- CSV output contains one row per control with linked evidence and exception summaries
- JSON output preserves summary counts and nested evidence and exceptions
- invalid provider, environment, evidence-source provider, and resource-reference values are rejected
- provider totals and coverage gaps appear in generated formats

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

Stable/default branch:

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
make verify
git push -u origin short-description
```

## Near-Term Roadmap

See [ROADMAP.md](../ROADMAP.md) for the staged implementation plan and completion criteria.
