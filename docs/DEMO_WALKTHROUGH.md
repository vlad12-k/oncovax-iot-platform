# Demo Walkthrough

## 1) Walkthrough intent

This document provides a guided walkthrough of the current OncoVax repository baseline.

The goal is to demonstrate implemented architecture, runtime behavior, and operational proof surfaces in a clear and credible order.

## 2) How to frame the project at the start

Start with this framing:

- The repository implements a **production-style hosted baseline** for cold-storage telemetry monitoring workflows.
- Telemetry in this runtime is **software-simulated**.
- This is **not** a physical medical hardware deployment.
- This is **not** a certified clinical deployment.
- In production-like ingress mode, operational surfaces are protected by nginx route policy (public-safe vs protected paths).
- The hosted baseline, live-domain wiring model, and observability stack are implemented and document-backed.

## 3) Recommended walkthrough order

1. **README and project framing**
   - Show scope, architecture summary, and explicit non-claims.
2. **Architecture diagram**
   - Walk through `docs/architecture-diagram.md` and service boundaries.
3. **Deployment model**
   - Explain dev, hosted baseline, and production-like ingress modes from `docs/DEPLOYMENT.md`.
4. **Runtime public-safe endpoint**
   - Show `/public-health` behavior through ingress.
5. **Internal API proof**
   - Show `/health`, `/summary`, and `/alerts` checks.
6. **Grafana/observability proof**
   - Show InfluxDB-backed telemetry/alert visibility and explain limits.
7. **Runbook / recovery / security posture**
   - Show `docs/RUNBOOK.md`, `OPS_RUNBOOK.md`, `docs/RECOVERY_AND_ROLLBACK.md`, and `SECURITY.md`.
8. **Known limitations and maturity boundaries**
   - Close with `docs/KNOWN_LIMITATIONS.md` and explicit next hardening priorities.

## 4) Proof surfaces to show

- **`/public-health`**
  - Demonstrates public-safe ingress liveness only.
- **`/summary` and `/alerts` API responses**
  - Demonstrate operational data visibility and alert workflow state exposure.
- **Grafana dashboards**
  - Demonstrate InfluxDB-backed time-series observability (telemetry and alert trends).
  - For visual evidence layering, prioritize live hosted screenshots in `docs/assets/live-hosted/` as the stronger hosted-runtime proof surface.
  - Use legacy demo/staged screenshots in `demo/screenshots/` as secondary supporting visuals only.
- **Architecture diagram**
  - Demonstrates implemented service boundaries, ingress, and persistence split.
- **Canonical docs (deployment, runbook, recovery, security, threat model)**
  - Demonstrate operational discipline, security posture, and recovery model coverage.

### Live hosted visual evidence to prioritize

When presenting observability proof in walkthroughs, use the deployed-baseline live hosted screenshots as the preferred visual layer before any legacy demo/staged visuals:

- `docs/assets/live-hosted/live-hosted-grafana-temperature-by-device.png`
- `docs/assets/live-hosted/live-hosted-grafana-recent-active-alerts-last-50.png`
- `docs/assets/live-hosted/live-hosted-grafana-telemetry-ingest-points-per-minute.png`
- `docs/assets/live-hosted/live-hosted-grafana-active-alerts-events-per-minute.png`

Keep framing conservative: these visuals strengthen runtime observability evidence, but they do not replace API/log/runbook validation and do not by themselves prove full production hardening or certification.

## 5) What to say about hosting and infrastructure

Describe hosting using implementation-backed statements:

- The platform supports a hosted cloud VM/server baseline.
- The production-like topology supports live custom-domain ingress.
- nginx ingress separates public-safe and protected operational routes.
- External uptime monitoring is useful as an availability signal for public-safe endpoint reachability.
- Atlas-backed persistence is supported via `MONGO_URI` configuration.

Avoid sharing raw admin console links or provider control-plane details during the walkthrough.

## 6) What to say about observability

- Grafana is useful for operational visibility, but it is not full operational truth.
- InfluxDB-backed dashboards show telemetry and alert-series trends.
- External uptime checks validate public endpoint reachability only.
- Full correctness still requires API checks, service status checks, and log review.

## 7) What not to claim

Do not claim:

- fully hardened production readiness
- certified medical/clinical deployment status
- complete security assurance
- physical device integration in this repository runtime

## 8) Closing guidance

End the walkthrough by summarizing what was proven and what remains intentionally bounded:

- proven: implemented architecture, ingestion-to-alert flow, protected ingress model, API proof surfaces, and observability workflow
- bounded: hardening maturity, application-layer auth depth, and operator-dependent deployment assurance

Close by pointing reviewers to:

- `docs/KNOWN_LIMITATIONS.md`
- `SECURITY.md`
- `docs/THREAT_MODEL.md`
- `docs/RUNBOOK.md`
- `docs/RECOVERY_AND_ROLLBACK.md`

This keeps the presentation credible, technically grounded, and aligned with current repository reality.
