# Observability Guide

## 1) Observability intent

This document defines the canonical observability model for the OncoVax repository baseline.

Observability in this repository provides baseline operational visibility for:

- telemetry activity
- alert-series activity
- service health checks
- ingress liveness checks

This is a practical baseline for engineering and operations workflows, not a claim of complete monitoring maturity.

## 2) Observability components

### InfluxDB (time-series source)

InfluxDB is the primary time-series observability source for:

- telemetry measurements
- alert-series measurements

### Grafana (observability surface)

Grafana provides dashboard-based visibility using InfluxDB-backed time-series data.

### API verification surfaces

Operational verification also relies on API checks:

- `GET /health`
- `GET /summary`
- `GET /alerts`

These checks validate operational behavior that dashboards alone do not fully prove.

### nginx public-health ingress visibility

In production-like ingress mode, nginx exposes `GET /public-health` as a narrow public-safe liveness route.

### External uptime monitoring

Operator-managed external uptime monitoring can continuously check public endpoint reachability for the hosted baseline domain.

## 3) What Grafana shows

Current Grafana coverage is primarily InfluxDB-driven and supports:

- telemetry trends over time
- alert-series visibility and trend signals
- metric-oriented panels for operational monitoring windows

Grafana is therefore useful for time-series signal visibility and trend interpretation across recent system behavior.

## 4) What Grafana does not represent

Grafana does not represent the full operational source of truth.

Specifically:

- Grafana is not the MongoDB lifecycle/audit truth boundary
- Grafana is not a substitute for API/runbook verification checks
- Grafana is not a claim of enterprise-grade monitoring completeness

Operational alert lifecycle and acknowledgement truth remains API/MongoDB backed.

## 5) External uptime monitoring

External uptime monitoring in this repository context is used for public-safe ingress reachability checks.

What it validates:

- the live public endpoint is reachable from outside the deployment perimeter
- the public-safe health route responds as expected

What it does not validate:

- full internal service correctness across worker, persistence, and operational API workflows
- protected-route behavior requiring authenticated operational checks
- complete incident-detection coverage for all failure modes

Treat uptime monitoring as one observability layer within an operator-managed monitoring posture.

## 6) Environment differences

Observability behavior differs by deployment mode.

### Local/dev (`infra/docker-compose.dev.yml`)

- includes InfluxDB and Grafana with direct local port exposure
- includes full local service visibility and local log inspection paths
- useful for dashboard iteration and end-to-end telemetry/alert inspection

### Hosted baseline (`infra/docker-compose.yml`)

- includes core services and InfluxDB
- does not include Grafana in this compose mode by default
- relies on API checks, container health/status, logs, and operator-managed monitoring integrations

### Production-like ingress (`infra/docker-compose.prod.yml` + nginx)

- includes InfluxDB and Grafana
- nginx provides ingress boundaries, including public-safe `GET /public-health`
- Grafana is a protected operational surface behind nginx basic-auth host routing
- protected API checks and runbook workflows remain required in addition to dashboard visibility

## 7) Operational verification path

Use runbook-aligned checks as the canonical verification path.

### Public ingress check

- `GET /public-health` through nginx to validate public-safe ingress liveness

### Internal API checks

- `GET /health`
- `GET /summary`
- `GET /alerts` (or constrained alert listing checks)

### Service state checks

- container logs for API/worker/nginx/simulator
- compose service status and health state checks

Canonical procedural references:

- `docs/RUNBOOK.md`
- `OPS_RUNBOOK.md`

## 8) Observability limitations

Current observability limitations include:

- dashboard maturity is evolving and should not be interpreted as exhaustive monitoring coverage
- monitoring is useful for baseline operations but is not exhaustive across all failure classes
- external uptime monitoring validates only one layer (public endpoint availability)
- the repository does not provide a full enterprise incident-detection platform
- observability tooling is not a substitute for disciplined human operational execution

## 9) Non-claims

Current observability support does not claim:

- physical medical device observability coverage
- certified clinical monitoring status
- fully hardened production monitoring completeness

Telemetry remains software-simulated in this repository runtime, and observability outcomes depend on correct operator-managed deployment and monitoring configuration.
