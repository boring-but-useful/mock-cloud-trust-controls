# Security And Design Principles

Mock Cloud Trust Controls is an evidence and reporting exercise, so trustworthiness matters more than feature count. These principles guide future AWS, Google Cloud, and provider-neutral work.

## Separate Intent From Implementation

A control describes the outcome the organization needs. Evidence describes how a particular system or cloud provider demonstrates that outcome.

```text
provider-neutral control -> provider-specific source -> normalized evidence -> validation -> report
```

Do not duplicate a control merely because AWS and Google Cloud use different service names. Create a provider-specific control only when the underlying requirement or risk is actually different.

## Make Trust Boundaries Explicit

Treat these inputs as untrusted:

- YAML control, evidence, and exception files
- Cloud API and command-line output
- Provider identifiers and resource metadata
- Imported scanner findings
- User-supplied paths, filters, dates, and configuration

Validate data before using it to make a control decision or generate a report. Do not silently coerce unknown states into passing results.

## Errors Versus Warnings

Errors mean the result cannot be trusted and must stop processing. Examples include malformed structure, missing required fields, unknown statuses, broken control references, invalid dates, and an approved exception that is already expired.

Warnings mean the data is structurally valid but needs timely human attention. The initial warning is an approved exception reaching its expiry date within 30 days. Warnings remain visible in command output and reports but do not change the process exit code.

Do not weaken an error into a warning merely to keep automation green.

## Preserve Evidence Provenance

Evidence should make it possible for a reviewer to answer:

- What control does this support?
- Which system and provider produced it?
- Which account, organization, folder, project, or environment did it cover?
- How and when was it collected?
- Who owns the source and the result?
- Can another reviewer reproduce the collection?

Store normalized summaries in the repository. Do not commit raw sensitive exports.

## Use Least Privilege

Future collectors should be read-only by default and request only the permissions needed for the selected evidence source. Prefer short-lived federation, workload identity, or ambient credentials over stored access keys or service-account keys.

Collection must remain an explicit action. Importing a module or running the test suite must never trigger a cloud API call.

## Handle Partial Failure Honestly

A collector that cannot inspect part of its intended scope must report incomplete coverage. It must not convert permission errors, throttling, pagination failures, or unsupported resources into a passing result.

Provider responses should be normalized only after collection metadata and failure state are preserved.

## Keep Output Deterministic

Given the same validated fixtures and reference date, report output should be stable. Sort provider results, statuses, controls, and resources where source ordering is not meaningful.

Generated artifacts belong in the same change as the inputs or code that produced them.

## Keep Dependencies Small

Use the Python standard library when it is clear and sufficient. Add a runtime dependency only when it removes meaningful complexity or risk. Pin supported version ranges and review transitive dependencies before adoption.

Provider SDKs should not become core dependencies until live collectors are implemented.

## Design For Testability

- Tests must run without network access or cloud credentials.
- Use synthetic sanitized fixtures for provider responses.
- Cover malformed inputs, unknown states, boundary dates, partial results, and failure paths.
- Inject dates, clients, and external boundaries when deterministic testing requires it.
- Keep one end-to-end fixture for each supported provider and control slice.

## Evolve The Architecture From Evidence

Keep the file-based workflow until it creates a demonstrated limitation. Do not add a database, service, web interface, plugin system, or generalized adapter framework preemptively.

Introduce a shared collector interface after two concrete collectors reveal the common contract. Prefer a complete vertical slice over many unfinished integrations.
