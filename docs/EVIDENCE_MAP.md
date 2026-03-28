# Evidence Map

## 1) Document intent

This document maps repository-level claims to concrete proof surfaces in the current OncoVax baseline.

Its purpose is to keep project positioning conservative, technically accurate, and evidence-backed.

## 2) How to read the evidence map

Each claim is documented with:

- **Claim**: what can be credibly stated from the current repository baseline.
- **Proof surface(s)**: where evidence exists (code, config, docs, checks).
- **What is demonstrated**: the specific behavior the evidence supports.
- **What is not demonstrated**: boundaries that remain outside the proof.

Use the map as a truth-boundary reference. If a statement is not supported by these proof surfaces, do not present it as established.

## 3) Canonical evidence map

### Claim A: A production-style hosted baseline exists

- **Proof surface(s)**
  - `README.md`
  - `docs/DEPLOYMENT.md`
  - `infra/docker-compose.yml`
  - `infra/docker-compose.prod.yml`
- **What is demonstrated**
  - Implemented deployment patterns exist for hosted baseline and production-like ingress topology.
  - Core service topology and operator-managed deployment context are documented and implemented.
- **What is not demonstrated**
  - Fully hardened production readiness.
  - Formal production assurance or certification.

### Claim B: Event-driven ingestion and processing architecture is implemented

- **Proof surface(s)**
  - `README.md`
  - `docs/ARCHITECTURE.md`
  - `docs/DATA_FLOW.md`
  - `docs/architecture-diagram.md`
- **What is demonstrated**
  - Implemented pipeline structure: simulator -> MQTT -> worker -> InfluxDB/MongoDB -> API/dashboard/Grafana.
  - Separation of time-series and operational persistence responsibilities.
- **What is not demonstrated**
  - Physical-device fleet ingestion proof.
  - Hardware lifecycle management capability.

### Claim C: A public-safe ingress route is implemented

- **Proof surface(s)**
  - `infra/nginx/nginx.conf` (`location = /public-health`)
  - `docs/DEPLOYMENT.md`
  - `docs/RUNBOOK.md`
  - `scripts/smoke_test.sh`
- **What is demonstrated**
  - `/public-health` is exposed through ingress as a narrow liveness route without basic auth.
  - The route is part of documented smoke/verification workflows.
- **What is not demonstrated**
  - Full internal service correctness.
  - Complete platform health or security posture.

### Claim D: Protected operational surfaces are implemented

- **Proof surface(s)**
  - `infra/nginx/nginx.conf`
  - `infra/docker-compose.prod.yml`
  - `SECURITY.md`
  - `docs/THREAT_MODEL.md`
- **What is demonstrated**
  - Operational API/dashboard routes and Grafana are protected by ingress basic-auth policy in production-like mode.
  - Route-level protections and selected rate limits are configured.
- **What is not demonstrated**
  - Complete application-layer authentication/authorization maturity.
  - End-to-end security assurance.

### Claim E: Operational API surfaces are implemented

- **Proof surface(s)**
  - `README.md`
  - `docs/RUNBOOK.md`
  - `OPS_RUNBOOK.md`
  - API route checks: `/health`, `/summary`, `/alerts`, acknowledgement workflow references
- **What is demonstrated**
  - API endpoints exist for liveness and operational alert workflow visibility.
  - Operational checks are documented for direct/local and production-like contexts.
- **What is not demonstrated**
  - Complete API governance/security model maturity.
  - Comprehensive SLA-backed production API operations.

### Claim F: Observability stack is implemented

- **Proof surface(s)**
  - `docs/OBSERVABILITY.md`
  - `infra/docker-compose.prod.yml` (Grafana + InfluxDB)
  - `README.md`
  - `grafana/` artifacts and provisioning references
- **What is demonstrated**
  - InfluxDB-backed telemetry and alert-series visibility via Grafana is implemented.
  - Observability interpretation boundaries are explicitly documented.
- **What is not demonstrated**
  - Exhaustive enterprise monitoring coverage.
  - Dashboard-only proof of full operational correctness.

### Claim G: Restart/recovery/runbook discipline is documented and demonstrable

- **Proof surface(s)**
  - `docs/RUNBOOK.md`
  - `OPS_RUNBOOK.md`
  - `docs/RECOVERY_AND_ROLLBACK.md`
  - `scripts/smoke_test.sh`
- **What is demonstrated**
  - Canonical verification, restart, recreate, and rollback procedures are documented.
  - Post-change validation sequences are defined for ingress, API, logs, and observability checks.
- **What is not demonstrated**
  - Zero-touch autonomous operations.
  - Guaranteed full restoration in all failure scenarios.

### Claim H: Atlas-backed persistence compatibility exists

- **Proof surface(s)**
  - `README.md`
  - `docs/DEPLOYMENT.md`
  - `docs/ARCHITECTURE.md`
  - `docs/DATA_FLOW.md`
- **What is demonstrated**
  - `MONGO_URI`-based Atlas-backed operational persistence is supported in hosted baseline guidance.
  - API/worker operational persistence model is documented with Atlas-compatible configuration.
- **What is not demonstrated**
  - Atlas-side operational guarantees independent of operator configuration.
  - Managed-database governance/certification outcomes.

### Claim I: Live custom-domain ingress model exists as hosted baseline context

- **Proof surface(s)**
  - `infra/nginx/nginx.conf` (`oncovax.live`, TLS certificate paths)
  - `docs/DEPLOYMENT.md`
  - `docs/RUNBOOK.md`
- **What is demonstrated**
  - Live-domain/TLS ingress wiring model is implemented and documented.
  - Public-safe and protected route behavior is explicitly separated in ingress policy.
- **What is not demonstrated**
  - Universal correctness across all operator environments.
  - Fully complete internet-facing hardening.

### Claim J: External uptime monitoring exists as an availability signal layer

- **Proof surface(s)**
  - `docs/OBSERVABILITY.md`
  - `docs/RUNBOOK.md`
  - `docs/DEMO_WALKTHROUGH.md`
- **What is demonstrated**
  - External uptime checks are treated as one operational signal for public endpoint reachability.
  - Documentation clearly scopes uptime monitoring to availability signaling.
- **What is not demonstrated**
  - End-to-end correctness of internal processing and persistence.
  - Complete incident detection across all failure modes.

## 4) Explicit non-evidence boundaries

The current repository baseline does **not** provide evidence for:

- certified clinical or regulated deployment status
- physical medical device fleet integration proof
- complete production hardening proof
- complete security assurance proof
- full internal correctness from public endpoint liveness alone

These boundaries must be stated explicitly in walkthroughs and documentation reviews.

## 5) Usage guidance

Use this document as a conservative claim-control reference:

- during walkthroughs, pair each claim with its listed proof surface before stating it
- during documentation review, reject statements that exceed documented proof boundaries
- keep claims implementation-backed and environment-aware
- use this file together with `README.md`, `docs/DEMO_WALKTHROUGH.md`, and `docs/DEMO_SCENARIOS.md` to maintain consistent, credible project positioning

Treat this evidence map as a maintained truth boundary for the repository baseline, not as a marketing summary.
