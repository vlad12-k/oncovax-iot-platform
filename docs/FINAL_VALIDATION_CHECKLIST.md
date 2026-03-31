# Final Validation Checklist

## 1) Document intent

This document is the canonical final validation checklist for the current OncoVax repository baseline.

Use it to verify runtime behavior, ingress controls, operational readiness discipline, documentation consistency, and claim boundaries before presenting or treating the repository as a stable hosted baseline.

## 2) Runtime validation

- [ ] **Compose service status is healthy for the target mode**
  - Local/dev: `docker compose -f infra/docker-compose.dev.yml ps`
  - Hosted baseline: `docker compose -f infra/docker-compose.yml ps`
  - Production-like: `docker compose -f infra/docker-compose.prod.yml ps`
- [ ] **Container health states are acceptable**
  - `docker ps --format "table {{.Names}}\t{{.Status}}"`
  - No sustained restart loops or unhealthy core services.
- [ ] **Public-safe ingress response is valid (production-like mode)**
  - `curl -iS https://<live-domain>/public-health`
  - Expect HTTP 200 and `{"status":"ok"}`.
- [ ] **Internal API checks pass**
  - `GET /health`
  - `GET /summary`
  - `GET /alerts`
  - Use direct/local or container-internal paths as documented in `docs/RUNBOOK.md`.
- [ ] **Observability sanity checks pass**
  - Telemetry and alert-series visibility in Grafana/InfluxDB path where Grafana is present.
  - Dashboard interpretation is consistent with API and logs (not dashboard-only conclusions).
- [ ] **Log sanity checks pass**
  - Review nginx/API/worker/simulator logs for active errors and repeated failure loops.

## 3) Ingress and protection validation

- [ ] **Public-safe route behavior is narrow and correct**
  - `/public-health` remains a liveness-style route, not a broad operational surface.
- [ ] **Protected operational surfaces remain protected**
  - Operational API/dashboard routes behind ingress require valid credentials.
- [ ] **Protected write path assumptions remain intact**
  - Alert acknowledgement route remains protected and write-rate-limited per nginx policy.
- [ ] **Grafana protection assumptions remain intact (production-like mode)**
  - Grafana host route remains access-controlled.

## 4) Documentation validation

- [ ] **Top-level canonical docs are aligned and non-contradictory**
  - `README.md`, `SECURITY.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/OVERVIEW.md`
  - `docs/ARCHITECTURE.md`, `docs/DATA_FLOW.md`, `docs/DEPLOYMENT.md`, `docs/OBSERVABILITY.md`
  - `docs/RUNBOOK.md`, `docs/THREAT_MODEL.md`, `docs/RECOVERY_AND_ROLLBACK.md`, `OPS_RUNBOOK.md`
  - `docs/DEMO_WALKTHROUGH.md`, `docs/DEMO_SCENARIOS.md`, `docs/EVIDENCE_MAP.md`
- [ ] **No stale process-era wording remains**
  - Remove prompt/sprint/phase/academic/recruiter/instructor/process-history language.
- [ ] **Claims are consistent with `docs/EVIDENCE_MAP.md`**
  - No claim is stated without an evidence-backed proof surface.
- [ ] **Non-claims remain explicit**
  - Non-clinical scope, simulated telemetry, and incomplete hardening/security assurance remain clearly stated.

## 5) Walkthrough/demo validation

- [ ] **Walkthrough sequence matches actual implementation**
  - `docs/DEMO_WALKTHROUGH.md` aligns with current architecture, deployment, and verification behavior.
- [ ] **Demo scenarios remain proof-backed**
  - `docs/DEMO_SCENARIOS.md` scenarios map to implemented routes/services/checks.
- [ ] **Evidence positioning stays aligned**
  - `docs/EVIDENCE_MAP.md` claims and non-claims match walkthrough framing and scenario language.

## 6) Operational validation

- [ ] **Runbook and operator quick reference remain aligned**
  - `docs/RUNBOOK.md` and `OPS_RUNBOOK.md` commands/interpretation are consistent.
- [ ] **Restart/recovery/rollback guidance remains consistent**
  - `docs/RECOVERY_AND_ROLLBACK.md` procedures align with current compose and ingress behavior.
- [ ] **Uptime interpretation remains availability-only**
  - External uptime is treated as reachability signal, not full internal correctness proof.
- [ ] **Canonical smoke path remains valid for production-like checks**
  - `./scripts/smoke_test.sh --prod <domain> <username> <password>` behavior aligns with runbook expectations.

## 7) Scope boundary validation

- [ ] **Simulated telemetry wording is explicit**
  - Documentation consistently states telemetry is software-simulated in repository runtime.
- [ ] **Non-clinical status is explicit**
  - Documentation consistently states this is not certified clinical infrastructure.
- [ ] **No overclaiming of production maturity**
  - No statements imply fully hardened production readiness.
- [ ] **No overclaiming of security assurance**
  - No statements imply complete security assurance or formal certification.

## 8) Out-of-scope / non-claims

This checklist does **not** certify or guarantee:

- certified clinical or regulated deployment status
- physical medical device fleet integration proof
- complete production hardening
- complete security assurance or formal security certification
- guaranteed full incident prevention or guaranteed full recovery
- full internal correctness from public endpoint liveness checks alone

Passing this checklist indicates baseline implementation and operational-validation consistency for the current repository scope; it does not elevate the project beyond the documented boundaries above.
