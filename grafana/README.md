# Grafana Subsystem

## Purpose

In this repository, Grafana is the dashboard-based **observability surface** for time-series signals.

It is used to:

- visualize telemetry and alert-series trends
- interpret recent runtime-window behavior
- support operator-oriented signal inspection during verification and troubleshooting

Grafana is useful for visibility, but it is **not** the sole operational source of truth.

## Data source and dependency model

Grafana in this repository is InfluxDB-backed.

- Primary datasource path: InfluxDB (Flux) time-series data
- Provisioning artifacts live under:
  - `grafana/provisioning/datasources/`
  - `grafana/provisioning/dashboards/`
  - `grafana/dashboards/`
- Correct datasource mapping, org/bucket alignment, and token/config quality are required for meaningful dashboard output

Operational boundary reminders:

- Grafana is **not** the MongoDB lifecycle/audit truth source
- MongoDB-backed operational lifecycle and acknowledgement truth remains outside dashboard panels
- API and persistence-backed workflow state remains authoritative for operational lifecycle interpretation

## What the dashboards show

Current dashboards are oriented to practical baseline observability and typically provide:

- telemetry trends over time
- alert-series visibility signals
- metric-level time-series panels
- recent-window runtime interpretation across active services

Dashboard output should be interpreted as signal visibility over selected time windows, not as exhaustive system proof.

## What Grafana does not prove

Grafana does **not** prove:

- full internal correctness of worker, API, and persistence behavior
- complete incident detection coverage
- protected-route correctness by itself
- acknowledgement/lifecycle correctness in MongoDB-backed workflows

Grafana is **not** a substitute for:

- API verification checks (`/health`, `/summary`, `/alerts`)
- runbook-driven restart/recovery validation
- container/log-based operational investigation

## Environment notes

### Local/dev (`infra/docker-compose.dev.yml`)

- Grafana is included and directly reachable on local port `3000`
- Useful for dashboard iteration and local runtime signal inspection
- Direct local access does not represent production-like ingress protections

### Hosted baseline (`infra/docker-compose.yml`)

- Core hosted baseline excludes Grafana by default
- Observability in this mode relies on API checks, logs, and operator-managed monitoring integrations

### Production-like ingress (`infra/docker-compose.prod.yml` + nginx)

- Grafana is included and mounted with repo-controlled provisioning/dashboards
- Grafana is exposed through nginx host routing (`grafana.<domain>`) and protected with basic-auth
- Access assumptions are operational/protected, not anonymous public dashboard access

## Operational cautions

- Time-range selection matters; incorrect windows can hide or misrepresent active behavior
- "No data" can result from multiple causes (quiet interval, ingestion interruption, datasource mismatch, or configuration errors)
- Datasource and dashboard provisioning alignment must match active runtime configuration
- Dashboard interpretation should be cross-checked against API responses and logs
- Protected operational access expectations still apply in hosted ingress environments

## Scope boundary reminder

- Telemetry in this repository is software-simulated
- Repository scope is non-clinical
- Grafana provides baseline observability, not complete monitoring assurance
- This subsystem should not be presented as certified clinical monitoring or fully hardened production monitoring

## Related references

- Repository entrypoint: `README.md`
- Observability model: `docs/OBSERVABILITY.md`
- Deployment model: `docs/DEPLOYMENT.md`
- Runbook procedures: `docs/RUNBOOK.md` and `OPS_RUNBOOK.md`
- Recovery/rollback: `docs/RECOVERY_AND_ROLLBACK.md`
- Evidence boundaries: `docs/EVIDENCE_MAP.md`
- Security and threat boundaries: `SECURITY.md`, `docs/THREAT_MODEL.md`
