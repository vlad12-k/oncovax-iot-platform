# Demo Screenshot Evidence Index

## Purpose

This directory contains screenshot-based demo and evidence artifacts for the repository baseline.

These images are supporting artifacts for walkthrough and review workflows. They are useful for visual context, but they are not the sole proof source.

## How to use this directory

Use screenshots together with canonical docs:

- demo flow and narration: `docs/DEMO_WALKTHROUGH.md`
- scenario framing and boundaries: `docs/DEMO_SCENARIOS.md`
- claim-to-proof boundaries: `docs/EVIDENCE_MAP.md`
- operational verification procedures: `docs/RUNBOOK.md` and `OPS_RUNBOOK.md`

Treat screenshots as supporting evidence layers. Final operational truth still depends on API checks, logs, runbook validation, and configuration-backed runtime behavior.

## Screenshot categories

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

Screenshots in this directory can support:

- visual confirmation that interfaces and operational views exist
- examples of observability/dashboard surfaces
- examples of API and operational workflow interaction patterns
- hosted-baseline evidence context for walkthrough discussions

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
- keep this index synchronized with actual files present in `demo/screenshots/`
