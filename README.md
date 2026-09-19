# Mock Cloud Trust Controls

A small, public-safe security control framework designed for evidence-driven cloud trust and compliance automation.

The project starts with readable YAML control definitions, mock evidence, exception examples, a validator, and Markdown, CSV, and JSON report generation.

This is a personal portfolio and learning project. External feedback is welcome, but the project is not maintained as a community-supported compliance product.

## AI-Assisted Development

This project was developed with AI-assisted tooling for research, design exploration, implementation support, documentation, and review. Project direction, architecture decisions, testing requirements, and final changes are reviewed and owned by the maintainer.

## Project Structure

```text
mock_cloud_trust_controls/
├── .github/
│   ├── dependabot.yml
│   └── workflows/verify.yml
├── .python-version
├── AGENTS.md
├── README.md
├── LICENSE
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

## Control Flow

```text
control intent -> requirement -> evidence -> test -> exception -> report
```

## Current Scope

- Ten provider-neutral controls, including three FinOps and cost-governance controls
- Seventeen synthetic evidence records, including an eight-record AWS/GCP/common logging review
- Four synthetic exception records demonstrating active and expired review states
- One complete multi-cloud logging vertical slice covering generation, routing, retention, delivery health, and queryability
- Provider-aware provenance, scope, environment, status, ownership, and coverage-gap analysis
- FinOps evidence for allocation, budgets/anomalies, and reliability-aware optimization
- A committed [architecture diagram and AWS/GCP walkthrough](docs/CLOUD_LOGGING_ARCHITECTURE.md), with editable Mermaid source and rendered SVG
- Python validation plus auditable Markdown, CSV, and JSON report generation
- Automated tests, report-drift detection, dependency maintenance, CodeQL, secret scanning, and protected-branch CI
- Generic illustrative framework references; no claim of official framework coverage
- No live cloud collectors, production data, employer data, or committed cloud credentials

## Usage

From this directory:

```bash
python3 -m pip install -r requirements.txt
make verify
```

For an isolated local environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
make verify
```

On Debian or Ubuntu, install the distribution's `python3-venv` package first if virtual-environment creation reports that `ensurepip` is unavailable.

`make verify` runs current-date strict validation, checks local Markdown links, regenerates all sample reports using the deterministic `SAMPLE_AS_OF` date, checks the committed reports for drift, and runs the complete test suite.

Individual commands remain available:

```bash
make validate
make docs
make report
make test
```

The committed sample snapshot defaults to `2026-09-18`. Override it deliberately when refreshing the sample review date:

```bash
make report SAMPLE_AS_OF=2026-10-01
```

The validator checks required fields and types, provider and environment values, synthetic scope metadata, duplicate IDs, allowed statuses, ISO dates, expired exceptions, evidence samples, and control references. Valid but time-sensitive conditions are emitted as non-blocking review warnings. Invalid YAML and missing inputs produce controlled errors instead of tracebacks.

Useful command-line options:

```bash
# Reproduce a review as of a specific date.
python3 scripts/validate_controls.py --as-of 2026-09-18

# Treat warnings as failures in automation.
python3 scripts/validate_controls.py --strict-warnings

# Write a report to another location without risking partial output.
python3 scripts/generate_report.py --output build/review/report.md

# Generate spreadsheet-friendly and machine-readable formats.
python3 scripts/generate_report.py --format csv
python3 scripts/generate_report.py --format json

# Combine a format with a custom destination.
python3 scripts/generate_report.py --format csv --output build/review/controls.csv
```

Markdown is the default human review document. CSV is a flat, one-row-per-control summary for spreadsheets. JSON preserves the complete nested control, evidence, exception, warning, provider-coverage, and summary data for automation. Reports include the effective review date and identify provider evidence gaps. The selected format determines the default destination under `reports/`; `--output` overrides it.

The report generator validates its input before writing and replaces the destination atomically, preserving the previous report if validation or writing fails. All three formats use only the Python standard library beyond the project's existing YAML dependency.

GitHub Actions runs `make verify` for pull requests, pushes to `main`, a weekly UTC schedule, and manual dispatches. The scheduled run surfaces time-dependent exception warnings or failures even when the repository is otherwise quiet. Dependabot checks the pinned Python dependency and pinned GitHub Actions weekly.

## Security And Design

- [SPEC.md](docs/SPEC.md) defines the project requirements, data model, validation rules, and acceptance criteria.
- [CODE_WALKTHROUGH.md](docs/CODE_WALKTHROUGH.md) explains how validation, report generation, and repository components fit together.
- [DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md) defines trust boundaries, validation behavior, evidence provenance, least privilege, failure handling, dependency policy, and testing expectations.
- [CLOUD_LOGGING_ARCHITECTURE.md](docs/CLOUD_LOGGING_ARCHITECTURE.md) diagrams the AWS/GCP evidence paths and compares coverage, routing, retention, integrity, delivery health, cost, and review trade-offs.
- [FINOPS_CONTROL_GUIDE.md](docs/FINOPS_CONTROL_GUIDE.md) explains allocation, budgets and anomalies, reliability-aware optimization, provider mappings, and review questions.
- [PROVIDER_EVIDENCE_MODEL.md](docs/PROVIDER_EVIDENCE_MODEL.md) defines provider fields, coverage semantics, the current migration, and deferred collector work.
- [SECURITY.md](SECURITY.md) defines safe reporting, sensitive-data rules, and requirements for future cloud collectors.
- [AGENTS.md](AGENTS.md) keeps the repository workflow and engineering guardrails durable across future work sessions.

## Roadmap And Current Work

The staged implementation plan is maintained in [ROADMAP.md](ROADMAP.md).

The provider-aware evidence model and AWS/GCP logging vertical slice are complete. The next engineering decision is whether read-only cloud collectors add enough value to justify their credential, API, and abstraction boundaries.

## License

This project is available under the [MIT License](LICENSE).
