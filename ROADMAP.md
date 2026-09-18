# Mock Cloud Trust Controls Roadmap

This roadmap keeps the project small enough to understand while growing it into a useful multi-cloud evidence and control-automation portfolio piece.

The design rule is:

```text
provider-neutral control objective -> provider-specific evidence -> normalized result -> reviewable report
```

AWS and Google Cloud should usually provide different evidence for the same control. Provider-specific controls should be added only when the underlying control objective is genuinely different.

## Current Baseline

- Seven YAML control definitions
- Seven synthetic evidence records
- Three synthetic exception records
- Local validation and Markdown report generation
- Unit tests for the validator and report generator
- Public-safe data only
- No live cloud credentials or API calls

## Phase 1 - Finish The Tested Baseline

Goal: land the existing requirements, documentation, and test work before starting another feature slice.

Completion criteria:

- `requirements.txt` documents the runtime dependency.
- Validator and report-generator tests pass.
- README, specification, and walkthrough agree with the repository state.
- The branch has no uncommitted changes.
- The feature branch is pushed and reviewed before merging to `main`.

## Phase 2 - Strengthen Data Integrity

Goal: make invalid or stale evidence visible before adding more providers and records.

Planned work:

1. Constrain evidence and exception statuses to documented values.
2. Validate evidence collection dates and exception expiry dates as ISO `YYYY-MM-DD` dates.
3. Detect approved exceptions whose expiry date has passed.
4. Distinguish validation errors from review warnings where appropriate.
5. Make report generation stop when its input fails validation.
6. Add report sections for active and expired exceptions.
7. Add negative tests for invalid status, malformed date, expired exception handling, malformed YAML roots, and invalid field types.
8. Update the documentation and generated sample report.

Completion criteria:

- Structurally invalid data causes validation and report generation to fail.
- An expired approved exception is clearly reported and cannot silently appear current.
- Current sample data intentionally demonstrates at least one active and one expired exception.
- Tests cover the new validation and reporting behavior.

## Phase 3 - Introduce A Multi-Cloud Evidence Model

Goal: support AWS, Google Cloud, and provider-neutral evidence without duplicating common control intent.

Planned evidence fields:

- `provider`: `aws`, `gcp`, or `common`
- `scope`: synthetic account, organization, folder, or project reference
- `environment`: such as `production`, `staging`, or `shared`
- `source_system`: provider service or common system
- `resource_ref`: optional synthetic resource reference

Planned behavior:

- Evidence-source definitions identify their provider.
- Reports roll up evidence by provider, control, status, and owner.
- Reports identify provider coverage gaps.
- Existing public-safe rules continue to apply to all fixtures.

## Phase 4 - Deepen The AWS Examples

Goal: replace one-record summaries with richer synthetic evidence that demonstrates review judgment.

Initial sources:

- AWS IAM and the configured identity provider
- AWS CloudTrail and log-retention settings
- AWS Config exposure findings
- AWS Security Hub findings
- Terraform, source-control, and CI/CD evidence

The fixtures should include passing evidence, review-needed evidence, missing coverage, and time-bound exceptions.

## Phase 5 - Add A Google Cloud Vertical Slice

Goal: prove the multi-cloud model with one complete control before broadening coverage.

Start with `MCTC-LOG-01`:

- AWS CloudTrail configuration and retention evidence
- Google Cloud Audit Logs configuration, coverage, routing, and retention evidence
- Provider-specific caveats documented beside the common control objective
- Combined validation and reporting

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

- Run validation and tests in GitHub Actions.
- Detect generated-report drift.
- Add CSV output after the reporting model stabilizes.
- Add a small architecture diagram.
- Add an AWS/Google Cloud comparison walkthrough.
- Document local setup, test commands, design choices, limitations, and safe credential handling.

## Scope Guardrails

- Do not turn the project into a full cloud-security platform.
- Do not add a database or web interface until the file-based workflow becomes a real limitation.
- Do not create provider adapter abstractions before the first live collector needs them.
- Do not claim official framework coverage without checking current primary sources.
- Do not use real employer, customer, account, project, or vulnerability data.
- Prefer one complete vertical slice over many shallow service mappings.

## Immediate Next Action

After the tested baseline branch is reviewed, create a short-lived data-integrity branch and implement date/status validation plus expired-exception reporting as the first Phase 2 slice.
