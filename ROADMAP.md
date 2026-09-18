# Mock Cloud Trust Controls Roadmap

This roadmap keeps the project small enough to understand while growing it into a useful multi-cloud evidence and control-automation portfolio piece.

The design rule is:

```text
provider-neutral control objective -> provider-specific evidence -> normalized result -> reviewable report
```

AWS and Google Cloud should usually provide different evidence for the same control. Provider-specific controls should be added only when the underlying control objective is genuinely different.

## Current Baseline

- Ten YAML control definitions
- Seventeen synthetic evidence records
- Four synthetic exception records
- Local validation and Markdown, CSV, and JSON report generation
- Provider-aware evidence provenance and coverage-gap reporting
- Unit tests for the validator and report generator
- Public-safe data only
- No live cloud credentials or API calls

## Phase 1 - Finish The Tested Baseline

Goal: land the existing requirements, documentation, and test work before starting another feature slice.

Status: complete.

Completion criteria:

- [x] `requirements.txt` documents the runtime dependency.
- [x] Validator and report-generator tests pass.
- [x] README, specification, and walkthrough agree with the repository state.
- [x] Completed baseline branches were pushed and reviewed before merging to `main`.

## Phase 2 - Strengthen Data Integrity

Goal: make invalid or stale evidence visible before adding more providers and records.

Status: complete.

Planned work:

- [x] Constrain evidence and exception statuses to documented values.
- [x] Validate evidence collection dates and exception expiry dates as ISO `YYYY-MM-DD` dates.
- [x] Detect approved exceptions whose expiry date has passed.
- [x] Distinguish validation errors from review warnings where appropriate.
- [x] Make report generation stop when its input fails validation.
- [x] Add report sections for active and expired exceptions.
- [x] Add negative tests for invalid status, malformed date, expired exception handling, malformed YAML roots, and invalid field types.
- [x] Update the documentation and generated sample report.

Completion criteria:

- [x] Structurally invalid data causes validation and report generation to fail.
- [x] An expired approved exception is clearly reported and cannot silently appear current.
- [x] Current sample data intentionally demonstrates at least one active and one expired exception.
- [x] Tests cover the new validation and reporting behavior.

Hardening checkpoint completed after Phase 2:

- Controlled invalid-YAML and missing-file errors
- Reproducible `--as-of` reviews
- Automation-friendly `--strict-warnings`
- Configurable and atomic report output
- One-command local verification and report-drift detection
- Least-privilege GitHub Actions verification
- Weekly Python and GitHub Actions dependency maintenance

## Phase 3 - Introduce A Multi-Cloud Evidence Model

Goal: support AWS, Google Cloud, and provider-neutral evidence without duplicating common control intent.

Status: complete. The model is documented in [PROVIDER_EVIDENCE_MODEL.md](PROVIDER_EVIDENCE_MODEL.md).

Implemented evidence fields:

- [x] `provider`: `aws`, `gcp`, or `common`
- [x] `scope`: synthetic account, organization, folder, or project reference
- [x] `environment`: `production`, `staging`, or `shared`
- [x] `source_system`: provider service or common system
- [x] `resource_ref`: optional synthetic resource reference

Implemented behavior:

- [x] Evidence-source definitions identify their provider.
- [x] Reports roll up evidence by provider, control, status, and owner.
- [x] Reports identify provider coverage gaps.
- [x] Reports record the effective review date.
- [x] Existing public-safe rules continue to apply to all fixtures.
- [x] Provider, environment, scope, and optional resource references are validated.
- [x] Markdown, CSV, and JSON expose provider coverage appropriately.

## Phase 4 - Deepen The AWS Examples

Goal: replace one-record summaries with richer synthetic evidence that demonstrates review judgment.

Status: complete for the first AWS logging vertical slice.

Initial sources:

- AWS IAM and the configured identity provider
- AWS CloudTrail and log-retention settings
- AWS Config exposure findings
- AWS Security Hub findings
- Terraform, source-control, and CI/CD evidence

The fixtures should include passing evidence, review-needed evidence, missing coverage, and time-bound exceptions.

Completed scope:

- [x] Split the broad `MCTC-LOG-01` record into CloudTrail configuration, S3 archive, SIEM ingestion, and saved-query evidence.
- [x] Demonstrate both passing evidence and a review-needed retention gap without inventing an exception for a control that prohibits one.
- [x] Complete the AWS and common evidence paths while preserving Google Cloud as the explicit provider gap.
- [x] Update validation expectations, generated reports, and documentation for the richer fixture set.

IAM, AWS Config, Security Hub, and infrastructure-change evidence can receive the same treatment later. They are not prerequisites for the focused Google Cloud logging slice.

## FinOps Interview-Practice Checkpoint

Status: complete.

- [x] Add provider-neutral controls for allocation and ownership, budgets and anomaly response, and reliability-aware optimization.
- [x] Add AWS and common synthetic evidence plus an approved capacity-headroom exception.
- [x] Declare comparable Google Cloud evidence sources without inventing GCP evidence.
- [x] Document provider mappings, design trade-offs, and a concise interview walkthrough in [FINOPS_CONTROL_GUIDE.md](FINOPS_CONTROL_GUIDE.md).

## Phase 5 - Add A Google Cloud Vertical Slice

Goal: prove the multi-cloud model with one complete control before broadening coverage.

Status: complete for `MCTC-LOG-01`.

Start with `MCTC-LOG-01`:

- AWS CloudTrail configuration and retention evidence
- Google Cloud Audit Logs configuration, coverage, routing, and retention evidence
- Provider-specific caveats documented beside the common control objective
- Combined validation and reporting

Completed scope:

- [x] Add organization-level Cloud Audit Logs configuration evidence with an explicit Data Access coverage gap.
- [x] Add a non-intercepting aggregated sink with child-resource coverage, reviewed exclusions, and destination permission.
- [x] Add a central Logging bucket with 365-day locked retention, customer-managed encryption, and restricted access.
- [x] Add sink-health metrics and a timestamped central audit-log query.
- [x] Document provider-specific behavior and make AWS, GCP, and common coverage complete for `MCTC-LOG-01`.

Then add:

1. IAM policies, service accounts, and central human access
2. VPC firewall rules and public-resource exposure
3. Cloud Asset Inventory evidence
4. Security Command Center findings
5. Common Terraform and CI/CD change evidence

## Phase 6 - Add Optional Read-Only Collectors

Goal: collect evidence from sandbox environments after the schema and reports are stable.

Principles:

- Start with one read-only collector per provider.
- Keep sanitized API responses as test fixtures.
- Normalize provider output into the common evidence schema.
- Use short-lived or ambient credentials rather than committed keys.
- Handle pagination, permission failures, partial results, and collection timestamps explicitly.
- Never require live cloud access to run the test suite or view the sample report.

Likely first collectors:

- AWS Config or CloudTrail configuration
- Google Cloud Asset Inventory or Cloud Audit Logs configuration

## Phase 7 - Automation And Portfolio Polish

Goal: make the repository easy to assess and demonstrate.

Planned work:

- [x] Run validation and tests in GitHub Actions.
- [x] Detect generated-report drift.
- [x] Add CSV and JSON output from a shared reporting model.
- Add a small architecture diagram.
- Add an AWS/Google Cloud comparison walkthrough.
- [x] Document local setup, test commands, design choices, limitations, and safe credential handling.

## Scope Guardrails

- Do not turn the project into a full cloud-security platform.
- Do not add a database or web interface until the file-based workflow becomes a real limitation.
- Do not create provider adapter abstractions before the first live collector needs them.
- Do not claim official framework coverage without checking current primary sources.
- Do not use real employer, customer, account, project, or vulnerability data.
- Prefer one complete vertical slice over many shallow service mappings.

## Immediate Next Action

Add the small architecture diagram and AWS/GCP comparison walkthrough from Phase 7. Use the completed `MCTC-LOG-01` evidence path as the concrete example, then evaluate optional read-only collectors without committing to a shared abstraction prematurely.
