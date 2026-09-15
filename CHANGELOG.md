# Changelog

All notable changes to this repository are documented in this file.

## [Unreleased]

No unreleased changes yet.

## v0.2.0 — Product Baseline & Deployment Lifecycle Release

Product-focused release hardening with archived hosting status, durable evidence naming, implementation-backed data contracts, repeatable local verification, and executable CI validation.

See [release notes](docs/RELEASE_NOTES_v0.2.0.md).

### Added

- Product-oriented release metadata and lifecycle documentation.
- Implementation-backed alert and audit-event data contracts.
- Contract, deployment, evidence-integrity, observability, and verification-entrypoint tests.
- Shared release-verification entrypoints through:
  - `make verify-static`
  - `make verify-local`
- nginx configuration validation using disposable local certificates.
- Repeatable end-to-end local pipeline verification covering telemetry, alert generation, API visibility, and acknowledgement.
- Archived DigitalOcean deployment lifecycle documentation and retained evidence references.

### Changed

- Reframed repository documentation around the implemented product architecture, operational behavior, verification paths, and explicit scope boundaries.
- Updated `README.md` and canonical documentation to distinguish:
  - local development
  - self-hosted baseline
  - TLS ingress topology
  - archived historical hosting evidence
- Aligned demo, walkthrough, and evidence documentation across:
  - `README.md`
  - `docs/EVIDENCE_MAP.md`
  - `docs/DEMO_WALKTHROUGH.md`
  - `docs/DEMO_SCENARIOS.md`
- Aligned operator and recovery documentation across:
  - `docs/RUNBOOK.md`
  - `OPS_RUNBOOK.md`
  - `docs/RECOVERY_AND_ROLLBACK.md`
  - `docs/OBSERVABILITY.md`
  - `docs/THREAT_MODEL.md`
- Renamed process-oriented evidence and documentation artifacts to durable product-oriented names while preserving historical evidence.
- Updated local development port exposure to loopback-only bindings.
- Updated CI so release validation runs repository tests, configuration checks, and local Docker runtime verification.
- Updated smoke-test behavior so HTTP failures propagate as failures.
- Updated Grafana provisioning and observability artifacts for repeatable local validation.
- Updated simulator documentation and configuration references to reflect actual runtime-loaded profiles and controls.

### Removed

- Process-specific prompt/sprint validation tests superseded by durable product-level verification tests.
- Unused device-metadata and multi-device-profile scaffolding not consumed by runtime.
- Redundant Docker build workflow superseded by consolidated release validation.
- Stale placeholder and superseded release-surface artifacts, including:
  - `demo/recording.gif`
  - `tools/postman_collection.json`
  - obsolete `.gitkeep` / `.keep` placeholder files

### Deployment lifecycle

- The previously validated DigitalOcean deployment is intentionally decommissioned after the available cloud credits were exhausted.
- Historical screenshots, checksums, configuration, runbooks, and recovery documentation remain archived as evidence.
- Historical domains and recordings are not presented as active service entrypoints.
- Future hosted deployment requires newly provisioned infrastructure, credentials, DNS, certificates, and environment-specific security validation.

### Verification

Release validation includes:

- `make verify-static`
- `make verify-local`
- pytest-based contract and repository checks
- Docker Compose configuration validation
- Python and shell syntax validation
- end-to-end local telemetry/alert/acknowledgement verification
- nginx configuration validation
- GitHub Actions release-validation checks

These checks establish the documented engineering baseline. They do not establish clinical certification, regulatory compliance, complete application-layer RBAC, immutable audit logging, or guaranteed disaster recovery.