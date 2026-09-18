# Mock Cloud Trust Controls - Sample Report

This report is generated from mock controls, evidence, and exception data. It is public-safe and illustrative only.

## Summary

- Review date: 2026-09-18
- Controls reviewed: 10
- Evidence items: 17
- Exceptions: 4

## Review Warnings

- No validation warnings.

## Evidence Status

- needs_review: 7
- pass: 10

## Exception Status

- approved: 2
- expired: 2

## Active Exceptions

- EX-IAM-001 (MCTC-IAM-02, expires 2027-09-18): Break-glass IAM user retained for recovery testing
- EX-COST-001 (MCTC-COST-03, expires 2026-12-31): Synthetic transaction database retains peak-capacity headroom

## Expired Exceptions

- EX-NET-001 (MCTC-NET-01, expired 2026-08-15): Temporary public endpoint for vendor validation
- EX-VULN-001 (MCTC-VULN-01, expired 2026-09-15): Medium dependency finding awaiting upstream patch

## Controls By Domain

- Cloud network exposure: 1
- FinOps and cost governance: 3
- Identity and access: 2
- Incident response and evidence handling: 1
- Infrastructure as code: 1
- Logging and monitoring: 1
- Vulnerability and configuration management: 1

## Evidence By Provider

- aws: 7 (needs_review: 4, pass: 3)
- gcp: 4 (needs_review: 1, pass: 3)
- common: 6 (needs_review: 2, pass: 4)

## Provider Coverage Gaps

- MCTC-COST-01: missing aws, gcp; current evidence: common
- MCTC-COST-02: missing gcp, common; current evidence: aws
- MCTC-COST-03: missing gcp, common; current evidence: aws
- MCTC-IAM-01: missing common; current evidence: aws
- MCTC-IAM-02: missing aws; current evidence: common
- MCTC-NET-01: missing common; current evidence: aws
- MCTC-VULN-01: missing common; current evidence: aws

## Evidence By Owner

- Platform: 1 (pass: 1)
- Platform / Finance: 2 (needs_review: 1, pass: 1)
- Platform / Finance / Service owners: 1 (needs_review: 1)
- Security / Compliance / Platform: 1 (pass: 1)
- Security / IT: 1 (needs_review: 1)
- Security / Platform: 9 (needs_review: 2, pass: 7)
- Security / Platform / Application team: 2 (needs_review: 2)

## Control Detail

### MCTC-COST-01: Cloud Spend Is Allocated And Owned

- Domain: FinOps and cost governance
- Owner: Platform / Finance / Service owners
- Review cadence: Monthly
- Automation status: Partial
- Exception allowed: True
- Objective: Make cloud spend attributable to accountable teams, services, and environments.
- Expected evidence providers: aws, gcp, common
- Current evidence providers: common
- Missing evidence providers: aws, gcp
- Evidence owners: Platform / Finance

Evidence:
- EV-COST-001 [common; shared; organization/example-company] (needs_review): Ninety-two percent of sampled spend is allocated; shared observability costs still need an approved allocation rule.

Exceptions:
- No open mock exception.

### MCTC-COST-02: Budgets Forecasts And Cost Anomalies Are Reviewed

- Domain: FinOps and cost governance
- Owner: Platform / Finance / Service owners
- Review cadence: Monthly
- Automation status: Partial
- Exception allowed: False
- Objective: Detect material cost variance early enough for accountable teams to respond.
- Expected evidence providers: aws, gcp, common
- Current evidence providers: aws
- Missing evidence providers: gcp, common
- Evidence owners: Platform / Finance

Evidence:
- EV-COST-002 [aws; production; organization/example-cloud] (pass): Production budgets and anomaly notifications route to accountable owners, and the sampled variance had a documented disposition.

Exceptions:
- No open mock exception.

### MCTC-COST-03: Cost Optimization Decisions Protect Reliability

- Domain: FinOps and cost governance
- Owner: Platform / Finance / Service owners
- Review cadence: Monthly
- Automation status: Partial
- Exception allowed: True
- Objective: Reduce avoidable spend without trading away required performance, resilience, or recovery capacity.
- Expected evidence providers: aws, gcp, common
- Current evidence providers: aws
- Missing evidence providers: gcp, common
- Evidence owners: Platform / Finance / Service owners

Evidence:
- EV-COST-003 [aws; production; account/example-production] (needs_review): Low-risk cleanup candidates are approved; a database rightsizing recommendation is deferred pending peak-load validation.

Exceptions:
- EX-COST-001 (approved, expires 2026-12-31): Synthetic transaction database retains peak-capacity headroom

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
- Current evidence providers: aws, gcp, common
- Missing evidence providers: none
- Evidence owners: Security / Platform

Evidence:
- EV-LOG-001 [aws; production; organization/example-cloud] (pass): The synthetic organization trail is multi-Region, covers member accounts, records read and write management events, uses SSE-KMS, and has log-file validation enabled.
- EV-LOG-002 [aws; production; organization/example-cloud] (needs_review): The synthetic archive is private, source-restricted, encrypted, and versioned, but its 180-day lifecycle is shorter than the documented 365-day retention requirement.
- EV-LOG-003 [common; production; organization/example-cloud] (pass): Sampled management events arrived within the synthetic ingestion objective, with no unexplained account or Region gaps during the review window.
- EV-LOG-004 [common; production; organization/example-cloud] (pass): The saved query returned expected administrative events with account, Region, actor, source, and event-time fields available for investigation.
- EV-LOG-005 [gcp; production; organization/example-google-cloud] (needs_review): Required audit logs are present and Data Access is enabled for designated services, but a newly adopted service lacks inherited DATA_READ coverage and needs owner and cost review.
- EV-LOG-006 [gcp; production; organization/example-google-cloud] (pass): The non-intercepting organization sink includes child resources, routes all audit-log types to the central project, has no security-log exclusions, and its dedicated writer can reach the destination.
- EV-LOG-007 [gcp; production; project/example-central-logging] (pass): The synthetic central bucket uses 365-day locked retention, customer-managed encryption, and restricted viewer access in the designated logging project.
- EV-LOG-008 [gcp; production; organization/example-google-cloud] (pass): The sampled sink shows routed entries without export errors, and the central query returns expected actor, resource, service, method, and event-time fields.

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
