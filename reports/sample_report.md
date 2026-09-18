# Mock Cloud Trust Controls - Sample Report

This report is generated from mock controls, evidence, and exception data. It is public-safe and illustrative only.

## Summary

- Review date: 2026-09-18
- Controls reviewed: 7
- Evidence items: 7
- Exceptions: 3

## Review Warnings

- No validation warnings.

## Evidence Status

- needs_review: 3
- pass: 4

## Exception Status

- approved: 1
- expired: 2

## Active Exceptions

- EX-IAM-001 (MCTC-IAM-02, expires 2027-09-18): Break-glass IAM user retained for recovery testing

## Expired Exceptions

- EX-NET-001 (MCTC-NET-01, expired 2026-08-15): Temporary public endpoint for vendor validation
- EX-VULN-001 (MCTC-VULN-01, expired 2026-09-15): Medium dependency finding awaiting upstream patch

## Controls By Domain

- Cloud network exposure: 1
- Identity and access: 2
- Incident response and evidence handling: 1
- Infrastructure as code: 1
- Logging and monitoring: 1
- Vulnerability and configuration management: 1

## Evidence By Provider

- aws: 4 (needs_review: 2, pass: 2)
- gcp: 0
- common: 3 (needs_review: 1, pass: 2)

## Provider Coverage Gaps

- MCTC-IAM-01: missing common; current evidence: aws
- MCTC-IAM-02: missing aws; current evidence: common
- MCTC-LOG-01: missing gcp, common; current evidence: aws
- MCTC-NET-01: missing common; current evidence: aws
- MCTC-VULN-01: missing common; current evidence: aws

## Evidence By Owner

- Platform: 1 (pass: 1)
- Security / Compliance / Platform: 1 (pass: 1)
- Security / IT: 1 (needs_review: 1)
- Security / Platform: 2 (pass: 2)
- Security / Platform / Application team: 2 (needs_review: 2)

## Control Detail

### MCTC-EVD-01: Evidence Is Source-Linked And Repeatable

- Domain: Incident response and evidence handling
- Owner: Security / Compliance / Platform
- Review cadence: Quarterly
- Automation status: Manual sample
- Exception allowed: True
- Objective: Make compliance evidence reproducible instead of screenshot-driven.
- Expected evidence providers: common
- Current evidence providers: common
- Missing evidence providers: none
- Evidence owners: Security / Compliance / Platform

Evidence:
- EV-EVD-001 [common; shared; organization/example-company] (pass): Sample evidence includes source system, collection method, date, owner, and reviewer path.

Exceptions:
- No open mock exception.

### MCTC-IAC-01: Infrastructure Changes Are Reviewed And Versioned

- Domain: Infrastructure as code
- Owner: Platform
- Review cadence: Monthly
- Automation status: Manual sample
- Exception allowed: True
- Objective: Make infrastructure changes reviewable and reproducible.
- Expected evidence providers: common
- Current evidence providers: common
- Missing evidence providers: none
- Evidence owners: Platform

Evidence:
- EV-IAC-001 [common; shared; organization/example-company] (pass): Sampled infrastructure changes include code review and deployment evidence.

Exceptions:
- No open mock exception.

### MCTC-IAM-01: Privileged Access Is Restricted

- Domain: Identity and access
- Owner: Security / Platform
- Review cadence: Quarterly
- Automation status: Partial
- Exception allowed: True
- Objective: Limit privileged access to approved users and roles.
- Expected evidence providers: aws, common
- Current evidence providers: aws
- Missing evidence providers: common
- Evidence owners: Security / Platform

Evidence:
- EV-IAM-001 [aws; production; account/example-production] (pass): Sample privileged roles have owners, approvals, and current business reasons.

Exceptions:
- No open mock exception.

### MCTC-IAM-02: Human Access Uses Central Authentication

- Domain: Identity and access
- Owner: Security / IT
- Review cadence: Quarterly
- Automation status: Partial
- Exception allowed: True
- Objective: Ensure human access is centrally managed and auditable.
- Expected evidence providers: aws, common
- Current evidence providers: common
- Missing evidence providers: aws
- Evidence owners: Security / IT

Evidence:
- EV-IAM-002 [common; production; organization/example-company] (needs_review): Central authentication is in place; one break-glass account requires recurring review evidence.

Exceptions:
- EX-IAM-001 (approved, expires 2027-09-18): Break-glass IAM user retained for recovery testing

### MCTC-LOG-01: Cloud Audit Logs Are Enabled And Retained

- Domain: Logging and monitoring
- Owner: Security / Platform
- Review cadence: Monthly
- Automation status: Partial
- Exception allowed: False
- Objective: Maintain a reliable audit trail for cloud activity.
- Expected evidence providers: aws, gcp, common
- Current evidence providers: aws
- Missing evidence providers: gcp, common
- Evidence owners: Security / Platform

Evidence:
- EV-LOG-001 [aws; production; organization/example-cloud] (pass): Audit logging is enabled and queryable for sampled production accounts.

Exceptions:
- No open mock exception.

### MCTC-NET-01: Internet Exposure Is Approved And Documented

- Domain: Cloud network exposure
- Owner: Security / Platform / Application team
- Review cadence: Monthly
- Automation status: Partial
- Exception allowed: True
- Objective: Reduce unintended public exposure of cloud resources.
- Expected evidence providers: aws, common
- Current evidence providers: aws
- Missing evidence providers: common
- Evidence owners: Security / Platform / Application team

Evidence:
- EV-NET-001 [aws; production; account/example-production] (needs_review): Most sampled public exposure has owners; one route requires refreshed approval.

Exceptions:
- EX-NET-001 (expired, expires 2026-08-15): Temporary public endpoint for vendor validation

### MCTC-VULN-01: Vulnerability Findings Are Triaged And Remediated

- Domain: Vulnerability and configuration management
- Owner: Security / Platform / Application team
- Review cadence: Monthly
- Automation status: Partial
- Exception allowed: True
- Objective: Ensure vulnerability and configuration findings are reviewed, owned, and remediated within defined expectations.
- Expected evidence providers: aws, common
- Current evidence providers: aws
- Missing evidence providers: common
- Evidence owners: Security / Platform / Application team

Evidence:
- EV-VULN-001 [aws; production; account/example-production] (needs_review): Critical and high findings are tracked; two medium findings require owner confirmation.

Exceptions:
- EX-VULN-001 (expired, expires 2026-09-15): Medium dependency finding awaiting upstream patch
