# Mock Cloud Trust Controls

A small, public-safe security control framework designed for evidence-driven cloud trust and compliance automation.

The project starts with readable YAML control definitions, mock evidence, exception examples, a simple validator, and a Markdown report generator.

## Project Structure

```text
mock_cloud_trust_controls/
├── AGENTS.md
├── README.md
├── SPEC.md
├── CODE_WALKTHROUGH.md
├── DESIGN_PRINCIPLES.md
├── ROADMAP.md
├── SECURITY.md
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

## Control Flow

```text
control intent -> requirement -> evidence -> test -> exception -> report
```

## Current Scope

- Seven starter controls
- YAML control definitions
- Mock evidence and exception examples
- Local validation and report generation
- Generic, illustrative framework references
- No claim of official framework coverage
- No production or employer data

## Usage

From this directory:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate_controls.py
python3 scripts/generate_report.py
python3 -m unittest discover -s tests
```

The validator checks required fields and types, duplicate IDs, allowed statuses, ISO dates, expired exceptions, evidence samples, and control references. Valid but time-sensitive conditions are emitted as non-blocking review warnings. The report generator validates its input before writing `reports/sample_report.md`.

## Security And Design

- [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) defines trust boundaries, validation behavior, evidence provenance, least privilege, failure handling, dependency policy, and testing expectations.
- [SECURITY.md](SECURITY.md) defines safe reporting, sensitive-data rules, and requirements for future cloud collectors.
- [AGENTS.md](AGENTS.md) keeps the repository workflow and engineering guardrails durable across future work sessions.

## Roadmap And Current Work

The staged implementation plan is maintained in [ROADMAP.md](ROADMAP.md).

The current engineering slice strengthens date and status validation, detects expired exceptions, and makes report generation reject invalid input. Multi-cloud evidence support follows that integrity work.
