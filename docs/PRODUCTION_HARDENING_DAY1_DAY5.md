# Production Hardening Plan (Day 1 to Day 5)

This document provides an additive hardening roadmap for the existing OncoVax deployment baseline. It is intended to improve operational posture without replacing current architecture.

## Scope and non-goals

- Keep current nginx reverse-proxy topology.
- Keep `/public-health` route available for uptime probes.
- Keep Basic Auth on restricted routes.
- Keep Docker Compose production deployment model.
- Do not commit secrets or runtime credentials.

## Day 1 — Access and secret hygiene

- Confirm all sensitive values come from environment variables.
- Verify `.env` files are excluded from version control.
- Rotate default dev credentials before non-local usage.
- Verify nginx auth file handling and file permissions.

## Day 2 — Network and transport controls

- Enforce HTTPS-only traffic at ingress.
- Review TLS certificate renewal process and alerting.
- Validate upstream timeout and body-size limits remain conservative.
- Confirm rate limits are enabled for read/write paths.

## Day 3 — Data and persistence controls

- Validate retention and backup settings for InfluxDB and MongoDB/Atlas.
- Ensure audit/event records include required timestamps and identifiers.
- Document restore test cadence and owner.

## Day 4 — Observability and incident readiness

- Add dashboards for telemetry and alert trend visibility.
- Define SLO-aligned probes for API and public-health endpoint.
- Add runbook links for alert triage and rollback actions.

## Day 5 — CI/CD and operational guardrails

- Add CI checks for required documentation and artifact structure.
- Add schema artifact presence checks.
- Add dry-run validation for exported dashboard/flow artifacts.
- Require review checklist confirmation for security-sensitive changes.

## Exit criteria

- Baseline deployment remains functional with unchanged auth and routing behavior.
- No secrets are committed.
- Required operational docs and artifact placeholders exist in-repo.
