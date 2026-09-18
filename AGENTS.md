# Mock Cloud Trust Controls Agent Notes

## Working Agreement

- Treat `main` as stable. Create short-lived branches from current `origin/main`; do not commit directly to `main`.
- Keep changes small, reviewable, and tied to one roadmap outcome.
- Update generated reports in the same change as the data or generator that produced them.
- Run validation, report generation, and the complete test suite before publishing a branch.

## Required Verification

From the repository root:

```bash
make verify
```

`make verify` uses strict warnings, checks generated-report drift, and runs all tests. Use the individual Python commands only when diagnosing one stage.

## Security Rules

- Use synthetic, public-safe data only.
- Never commit cloud credentials, tokens, secrets, real account or project identifiers, production evidence, or employer control language.
- Prefer read-only access and short-lived federation for any future cloud collector.
- Keep live cloud access optional. Tests and sample reports must run without network or cloud credentials.
- Treat YAML, cloud API responses, and collector output as untrusted input.
- Fail closed on malformed structure, unknown states, broken references, or stale approved exceptions.
- Do not print secrets or raw sensitive provider responses in errors, logs, fixtures, or reports.
- Minimize dependencies and justify each new runtime package.

## Design Rules

- Keep control intent provider-neutral unless the objective is genuinely provider-specific.
- Isolate AWS and Google Cloud collection details at the evidence-source or collector boundary.
- Normalize provider output before validation and reporting.
- Prefer deterministic file-based behavior until a database or service is demonstrably necessary.
- Preserve evidence provenance: source, scope, collection method, collection time, and ownership.
- Use errors for invalid or unsafe state. Use warnings only for valid state that needs timely review.
- Add negative tests for validation, authorization, malformed inputs, partial results, and failure handling.
- Avoid speculative abstractions. Introduce a shared interface when at least two concrete implementations need it.

## Documentation

- Keep `README.md`, `SPEC.md`, `CODE_WALKTHROUGH.md`, `ROADMAP.md`, `DESIGN_PRINCIPLES.md`, and `SECURITY.md` consistent with behavior.
- Document important trade-offs and rejected alternatives when the reason would not be obvious later.
