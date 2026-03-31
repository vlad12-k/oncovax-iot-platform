# Production Hardening Roadmap (Day 1 to Day 5)

## 1) Document intent

This document is the canonical staged hardening roadmap for the current OncoVax repository baseline.

It defines practical hardening priorities for a production-style hosted baseline and clarifies the difference between:

- controls already represented in the repository baseline
- additional hardening work that remains roadmap work

Roadmap items in this document are planning targets, not proof of completed controls.

## 2) Current baseline already represented

The current repository baseline already represents the following controls and operational patterns:

- ingress separation between a narrow public-safe route and protected operational surfaces
- protected operational API/dashboard and Grafana surfaces in production-like ingress policy
- TLS and domain ingress scaffolding in nginx-based topology
- selected nginx request limiting on protected and write-sensitive paths
- runbook, recovery/rollback, and final-validation checklist documentation
- observability baseline through InfluxDB, Grafana (where present), API checks, and log inspection guidance
- hosted baseline deployment model with production-like topology variant and Atlas-compatible operational persistence

These controls are meaningful baseline protections. They do not, by themselves, establish full production hardening.

## 3) Why additional hardening is still needed

Additional hardening remains necessary because current baseline limits are explicit:

- application-layer authentication and authorization (including RBAC depth) are incomplete
- env-file and environment-variable secret handling is practical but lower maturity than dedicated secrets systems
- security posture depends heavily on operator-managed perimeter controls (domain, TLS lifecycle, firewall scope, exposure boundaries)
- observability and incident-detection maturity is useful but not exhaustive
- recovery and rollback remain operator-driven procedures requiring disciplined execution

## 4) Day 1 to Day 5 staged roadmap

### Day 1 — Ingress, domain, TLS, and route-protection verification

- **Objective**
  - Verify that live ingress behavior matches documented public-safe vs protected boundaries.
- **What it improves**
  - Reduces immediate exposure risk from route-policy drift and TLS/domain misconfiguration.
  - Confirms protected operational surfaces remain access-controlled.
- **What remains out of scope after Day 1**
  - Full application-layer auth/RBAC maturity.
  - Full production security assurance.

### Day 2 — Perimeter controls and secret-hygiene tightening

- **Objective**
  - Tighten firewall/perimeter exposure and improve operational credential/secret handling discipline.
- **What it improves**
  - Shrinks avoidable attack surface from overly broad network exposure.
  - Lowers operational risk from weak credential and secret-handling practices.
- **What remains out of scope after Day 2**
  - Centralized enterprise secrets-management guarantees.
  - Formal compliance or certification outcomes.

### Day 3 — Application auth maturity and rate-limit posture review

- **Objective**
  - Prioritize first-class application-layer auth/authorization controls and review ingress rate-limit adequacy.
- **What it improves**
  - Reduces over-reliance on ingress-only controls.
  - Improves control depth for protected operational workflows.
- **What remains out of scope after Day 3**
  - Complete end-to-end identity/governance maturity.
  - Proof of comprehensive abuse-resistance across all workloads.

### Day 4 — Monitoring, alerting, and operational-visibility improvements

- **Objective**
  - Improve monitoring signal quality, alerting discipline, and runbook-linked observability interpretation.
- **What it improves**
  - Improves detection speed and operator confidence in diagnosing degradation.
  - Reduces false confidence from single-surface checks (for example uptime-only or dashboard-only conclusions).
- **What remains out of scope after Day 4**
  - Full enterprise-grade detection and response coverage.
  - Elimination of all monitoring blind spots.

### Day 5 — Recovery validation, resilience testing, and release-discipline checks

- **Objective**
  - Validate restart/recovery/rollback workflows through repeatable drills and tighten release-change validation discipline.
- **What it improves**
  - Improves operational readiness for service disruption and misconfiguration recovery.
  - Strengthens confidence that documented procedures work under realistic failure and rollback scenarios.
- **What remains out of scope after Day 5**
  - Guaranteed prevention of incidents.
  - Guaranteed complete data/service restoration in all failure classes.

## 5) Stage execution checklist template

Use this template for each stage before marking it complete:

- [ ] Objective is clearly defined and accepted by operators/maintainers
- [ ] Planned checks/changes are mapped to canonical docs (`SECURITY.md`, `docs/RUNBOOK.md`, `docs/RECOVERY_AND_ROLLBACK.md`, `docs/FINAL_VALIDATION_CHECKLIST.md`)
- [ ] Evidence of completion is captured in reproducible form (commands, configs, verification outputs)
- [ ] Remaining out-of-scope items are explicitly documented
- [ ] Claims are reviewed against `docs/EVIDENCE_MAP.md` boundaries before external presentation

## 6) Non-claims

This roadmap does **not** imply or certify:

- completion of all hardening work simply because roadmap stages are defined
- fully production-ready status
- certified clinical or regulated deployment status
- complete security assurance or formal security certification

Roadmap planning is not equivalent to demonstrated capability.

## 7) How to use this roadmap

Use this document as a hardening planning aid for staged execution.

Use it together with:

- `README.md`
- `SECURITY.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/THREAT_MODEL.md`
- `docs/RUNBOOK.md`
- `docs/RECOVERY_AND_ROLLBACK.md`
- `docs/FINAL_VALIDATION_CHECKLIST.md`
- `docs/EVIDENCE_MAP.md`

Apply conservative claim discipline:

- treat completed, evidence-backed controls as baseline facts
- treat planned or in-progress items as roadmap work
- avoid overstating hardening maturity beyond documented proof boundaries
