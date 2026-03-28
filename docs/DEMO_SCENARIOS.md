# Demo Scenarios

## 1) Document intent

This document lists canonical demo scenarios for the current OncoVax repository baseline.

Each scenario is selected to show implemented behavior with clear operational proof value and explicit scope boundaries.

## 2) Scenario selection principles

Use these principles when selecting scenarios:

- **Implemented only**: use scenarios that map directly to current services, routes, and runbook procedures.
- **Proof-backed only**: each scenario should be tied to concrete proof surfaces (endpoint behavior, API responses, dashboards, logs, runbook checks).
- **No overclaiming**: present what is demonstrated, and state what is not proven.
- **Baseline alignment**: scenario wording must match current hosted baseline, ingress policy, and canonical documentation.

## 3) Canonical demo scenarios

### Scenario A: Public-safe ingress liveness

- Show `GET /public-health` behavior through ingress.
- Validate expected liveness response for the public-safe route.

### Scenario B: Internal operational API behavior

- Show `GET /health`, `GET /summary`, and `GET /alerts` responses.
- Demonstrate that operational state is available through implemented API surfaces.

### Scenario C: Observability and Grafana visibility

- Show Grafana dashboards backed by InfluxDB time-series data.
- Confirm telemetry/alert trend visibility for the current runtime window.

### Scenario D: Alert visibility and operator workflow state

- Show alert visibility through API and dashboard surfaces.
- Show acknowledgement path behavior on protected operational routes.

### Scenario E: Protected operational surface posture

- Show that operational API/dashboard routes are protected by ingress policy.
- Show that Grafana operational access is protected in production-like topology.

### Scenario F: Restart/recovery validation path

- Show runbook-aligned restart/recovery checks.
- Validate post-restart behavior with ingress checks, API checks, and log review.

### Scenario G: Hosted baseline and operator-managed infrastructure context

- Frame hosted baseline characteristics: live domain model, TLS ingress, protected routes, and Atlas-backed persistence compatibility.
- Keep focus on implemented operator-managed infrastructure boundaries.

## 4) What each scenario proves

- **Scenario A (public-safe ingress liveness)** proves narrow ingress reachability for a public-safe endpoint.
- **Scenario B (internal API behavior)** proves operational API response correctness for health and summary/alert data access.
- **Scenario C (observability/Grafana)** proves InfluxDB-backed time-series visibility for telemetry and alert trends.
- **Scenario D (alert visibility/workflow)** proves alert-state visibility and implemented acknowledgement workflow behavior.
- **Scenario E (protected surfaces)** proves route-level protection posture for operational interfaces.
- **Scenario F (restart/recovery validation)** proves operational discipline and post-change verification process quality.
- **Scenario G (hosted baseline context)** proves the repository supports a realistic hosted deployment model with operator-managed controls.

These proof values are complementary and should be presented together when possible.

## 5) What each scenario does not prove

No scenario in this document should be presented as proof of:

- certified clinical or regulated deployment status
- physical medical device fleet integration in repository runtime
- complete security assurance or complete hardening
- full production maturity across all operational and governance dimensions

Additional boundaries to state clearly:

- public-safe liveness checks do not prove complete internal correctness
- dashboard visibility does not replace API/runbook/log verification
- hosted baseline support does not equal final production certification

## 6) Recommended usage

For a concise and credible walkthrough, select a small scenario set:

1. **Public-safe ingress liveness**
2. **Internal operational API behavior**
3. **Observability/Grafana visibility**
4. **Protected operational surface posture**
5. **Restart/recovery validation path** (time permitting)

Presentation guidance:

- Start with implementation-backed framing from `docs/DEMO_WALKTHROUGH.md`.
- Keep each scenario tied to a concrete proof surface.
- Distinguish liveness, API correctness, observability, and operational process evidence.
- End by reaffirming known limitations and hardening boundaries from canonical docs.
