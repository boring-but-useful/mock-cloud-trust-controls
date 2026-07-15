# Mock Cloud Trust Controls

A small, public-safe security control framework designed for evidence-driven cloud trust and compliance automation.

The project starts with readable YAML control definitions, mock evidence, exception examples, a simple validator, and a Markdown report generator.

## Project Structure

```text
mock_cloud_trust_controls/
├── README.md
├── catalog.md
└── controls/
    ├── MCTC-EVD-01.yaml
    ├── MCTC-IAC-01.yaml
    ├── MCTC-IAM-01.yaml
    ├── MCTC-IAM-02.yaml
    ├── MCTC-LOG-01.yaml
    ├── MCTC-NET-01.yaml
    └── MCTC-VULN-01.yaml
├── examples/
│   ├── mock_evidence.yaml
│   └── mock_exceptions.yaml
├── reports/
│   └── sample_report.md
└── scripts/
    ├── generate_report.py
    └── validate_controls.py
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
python3 scripts/validate_controls.py
python3 scripts/generate_report.py
```

The validator checks required fields, duplicate IDs, list fields, evidence samples, and exception references. The report generator writes `reports/sample_report.md`.

## Planned Next Steps

1. Add more realistic mock findings for AWS Config, Security Hub, IAM, and CloudTrail.
2. Add CSV report output for spreadsheet-style review.
3. Add severity and status rollups by domain.
4. Add official framework mappings only after checking current primary sources.
