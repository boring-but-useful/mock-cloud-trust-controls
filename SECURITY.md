# Security Policy

## Project Scope

Mock Cloud Trust Controls is a public-safe portfolio project built from synthetic controls, evidence, and exceptions. It is not a production compliance platform and should not contain real cloud exports or confidential control material.

The latest `main` branch is the supported version.

## Reporting A Security Issue

Do not include credentials, private cloud data, or exploit details in a public issue.

Use GitHub private vulnerability reporting when it is available for this repository. If it is unavailable, open a minimal issue requesting a private contact channel without disclosing sensitive details.

Include, when safe:

- affected file, command, or version
- expected and observed behavior
- security impact
- minimal reproduction using synthetic data
- suggested mitigation, if known

## Secrets And Sensitive Data

Never commit:

- AWS access keys, session tokens, or account exports
- Google Cloud service-account keys, access tokens, or project exports
- identity-provider secrets or membership exports
- real production evidence, findings, resource names, or customer information
- employer control language or confidential audit material

If a secret is committed, revoke or rotate it first. Removing it from the latest commit is not sufficient because it may remain in Git history and remote caches.

## Future Cloud Collectors

Collectors must:

- use read-only least-privilege permissions
- prefer short-lived federation or ambient credentials
- require an explicit collection command
- apply timeouts and bounded retries
- handle pagination and partial failure
- avoid logging tokens or raw sensitive responses
- keep sanitized fixtures separate from live output
- run no live calls during imports or tests

See [DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md) for the architectural rules that support these requirements.

## Build And Dependency Security

- Runtime dependencies are pinned and updated through reviewed pull requests.
- GitHub Actions are pinned to full commit identifiers.
- Workflow permissions default to read-only repository contents.
- Checkout credentials are not persisted after the checkout step.
- CI runs without repository or cloud secrets.
- Dependabot checks Python and GitHub Actions dependencies weekly.
