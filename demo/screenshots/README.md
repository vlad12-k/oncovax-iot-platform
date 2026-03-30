# Demo Screenshot Evidence Index

## Purpose

This index separates two screenshot evidence classes used in this repository baseline:

- **Legacy demo/staged screenshots** stored in `demo/screenshots/`
- **Live hosted evidence screenshots** stored in `docs/assets/live-hosted/`

Both classes are supporting artifacts for walkthrough and review workflows. They are useful for visual context, but they are not the sole proof source.

## How to use this index

Use screenshots together with canonical docs:

- demo flow and narration: `docs/DEMO_WALKTHROUGH.md`
- scenario framing and boundaries: `docs/DEMO_SCENARIOS.md`
- claim-to-proof boundaries: `docs/EVIDENCE_MAP.md`
- operational verification procedures: `docs/RUNBOOK.md` and `OPS_RUNBOOK.md`

Treat screenshots as supporting evidence layers. Final operational truth still depends on API checks, logs, runbook validation, and configuration-backed runtime behavior.

## Evidence classes

### A) Live hosted evidence (deployed baseline)

Path: `docs/assets/live-hosted/`

These screenshots are from the actually deployed, server-backed baseline and should be treated as the stronger visual evidence layer for hosted runtime observability.

Use these first when presenting hosted-baseline observability claims.

- `live-hosted-grafana-alert-intensity-value-minus-threshold.png`
- `live-hosted-grafana-telemetry-ingest-points-per-minute.png`
- `live-hosted-grafana-active-alerts-events-per-minute.png`
- `live-hosted-grafana-devices-seen-in-window.png`
- `live-hosted-grafana-recent-active-alerts-last-50.png`
- `live-hosted-grafana-door-open-state-distribution.png`
- `live-hosted-grafana-temperature-by-device.png`
- `live-hosted-grafana-humidity-and-battery-trends.png`
- `live-hosted-grafana-signal-strength-offline-pulse-visibility.png`
- `live-hosted-grafana-latest-metrics-by-device.png`

### B) Legacy demo/staged screenshots

Path: `demo/screenshots/`

These screenshots remain useful as supporting/illustrative visuals, but they are secondary to live hosted evidence when a hosted runtime claim is being presented.

Use these as secondary visuals only after showing live hosted evidence.

## Legacy demo/staged screenshot categories (`demo/screenshots/`)

### 1) Architecture / documentation visuals

- `prompt_g_fig_readme_quick_review_section.png`

Supports visual confirmation of repository documentation surface and entrypoint structure.

### 2) Grafana / observability visuals

- `sprint_11_fig_operational_dashboard_main_view.png`
- `sprint_11_fig_operational_dashboard_filtered_view.png`
- `sprint_11_fig_operational_dashboard_search_view.png`
- `sprint_12_fig_digitalocean_hosted_dashboard_view.png`

Supports dashboard-oriented observability examples (visibility/filter/search views and hosted dashboard context).

### 3) Operational UI / API proof visuals

- `sprint_7_fig_api_alerts_get_terminal.png`
- `sprint_7_fig_api_acknowledge_post_terminal.png`
- `sprint_7_fig_api_alerts_after_ack_terminal.png`
- `sprint_10_fig_api_single_alert_terminal.png`
- `sprint_10_fig_api_filtered_unacknowledged_alerts_terminal.png`
- `sprint_10_fig_api_summary_terminal.png`
- `sprint_4_fig_acknowledge_alert_script_terminal.png`
- `sprint_4_fig_mongodb_acknowledged_audit_event_terminal.png`

Supports visual examples of alert retrieval/acknowledgement flows and API-facing operational checks.

### 4) Deployment / ingress / hosted-baseline visuals

- `sprint_8_fig_docker_stack_with_api_container.png`
- `sprint_8_fig_containerized_api_health_terminal.png`
- `sprint_8_fig_smoke_test_with_api_check_terminal.png`
- `sprint_9_fig_env_example_configuration.png`
- `sprint_9_fig_api_healthcheck_configuration.png`
- `sprint_9_fig_api_healthcheck_healthy_stack.png`
- `sprint_12_fig_digitalocean_hosted_api_terminal.png`

Supports deployment and health-check context for local/containerized and hosted-baseline demonstration views.

### 5) Validation / persistence / operational context visuals

- `sprint_12_fig_atlas_api_summary_and_alerts_terminal.png`
- `sprint_12_fig_atlas_cluster_or_collection_view.png`
- `sprint_6_fig_nodered_flow_canvas.png`
- `sprint_6_fig_nodered_debug_messages.png`

Supports persistence/integration context and operational validation illustrations.

## What screenshots demonstrate

Screenshots referenced by this index can support:

- visual confirmation that interfaces and operational views exist
- examples of observability/dashboard surfaces
- examples of API and operational workflow interaction patterns
- hosted-baseline evidence context for walkthrough discussions (strongest when using `docs/assets/live-hosted/`)

## What screenshots do not prove

Screenshots alone do **not** prove:

- full runtime correctness
- complete security assurance
- complete production readiness
- certified clinical infrastructure
- full operational truth without API/log/runbook evidence

Screenshots should be interpreted as static evidence snapshots, not complete runtime verification.

## Naming and curation expectations

When adding or refreshing screenshot artifacts:

- prefer clear, neutral, release-grade names that describe the captured surface
- avoid process-history-oriented naming as primary evidence language
- avoid retaining outdated screenshots as default references when newer canonical evidence exists
- keep this index synchronized with actual files in both `demo/screenshots/` and `docs/assets/live-hosted/`
