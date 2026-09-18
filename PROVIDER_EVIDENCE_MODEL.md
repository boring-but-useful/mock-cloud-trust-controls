# Provider-Aware Evidence Model

## Decision

Controls remain provider-neutral. Provider details belong on evidence-source definitions and collected evidence records.

```text
provider-neutral control
    -> declared AWS, GCP, or common evidence source
    -> scoped evidence record
    -> validation
    -> provider rollup and coverage-gap report
```

This avoids creating separate AWS and Google Cloud controls when both providers support the same security objective.

## Evidence Fields

Every evidence record requires:

- `provider`: `aws`, `gcp`, or `common`
- `scope`: a public-safe account, organization, folder, project, or shared-system reference
- `environment`: `production`, `staging`, or `shared`
- `source_system`: the service or system that produced the evidence
- `collection_method`: how the evidence was collected
- `collection_date`: an ISO `YYYY-MM-DD` date
- `owner`, `status`, and `summary`

`resource_ref` is optional. When present, it must be a non-empty synthetic reference that helps a reviewer identify the sampled resource without exposing a real cloud identifier.

Control `evidence_sources` entries also require `provider`. The provider on a source describes where that evidence is expected to originate; it does not make the control itself provider-specific.

## Coverage Semantics

For each control:

1. Expected providers are derived from the control's declared evidence sources.
2. Current providers are derived from validated evidence linked by `control_id`.
3. A coverage gap is an expected provider with no linked evidence record.

A gap is not automatically a failed control. It is an explicit statement that the current sample does not demonstrate that declared evidence path. Evidence `status` continues to describe the result of an evidence record that actually exists.

## Current Evidence Set

The current thirteen records preserve provider-neutral control intent while showing provider-specific collection paths:

- AWS IAM, CloudTrail, S3, Config, Security Hub, budget, and optimization records use `provider: aws`.
- Identity-provider, source-control/CI, and control-repository records use `provider: common`.
- SIEM ingestion and saved-query records use `provider: common` even when their sampled events originated in AWS.
- Production cloud records use `environment: production`.
- Shared engineering and evidence systems use `environment: shared`.
- All scopes and resource references are synthetic and public-safe.

`MCTC-LOG-01` has complete AWS and common evidence paths. It declares Google Cloud Audit Logs as a GCP source, but no GCP record is invented before the planned vertical slice, so reports correctly preserve that provider gap.

## Reporting

- Markdown shows the review date, provider and owner totals, status counts, and per-control gaps.
- CSV adds the review date plus expected, present, and missing provider columns and evidence owners to each control row.
- JSON preserves the full provider-aware evidence records, provider summaries, and structured coverage gaps.

Committed sample reports use the fixed `SAMPLE_AS_OF` date from the `Makefile` so generated artifacts remain deterministic. Normal CLI use defaults to the current date unless `--as-of` is supplied.

## Deferred Work

- Richer AWS evidence for controls beyond `MCTC-LOG-01` can follow the same Phase 4 pattern later.
- The first real GCP evidence record belongs to the `MCTC-LOG-01` vertical slice in Phase 5.
- Provider SDKs and live read-only collection belong to Phase 6.
- A generalized collector interface should wait until two concrete collectors reveal a stable common contract.
