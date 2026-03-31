# Deployment Guide

## 1) Deployment intent

This document defines the canonical deployment model for the OncoVax repository baseline.

The repository supports three deployment patterns:

- local/dev deployment
- hosted baseline deployment
- production-like ingress deployment using nginx

Deployment support is practical and operationally useful, but it is not a claim of fully hardened production readiness.

## 2) Deployment modes

### Local/dev (`infra/docker-compose.dev.yml`)

Full local stack for development, testing, and operational workflow validation.

### Hosted baseline (`infra/docker-compose.yml`)

Core hosted stack for MQTT transport, worker processing, API, and persistence services.

### Production-like ingress path (`infra/docker-compose.prod.yml` + `infra/nginx/nginx.conf`)

Hosted stack with nginx reverse proxy, TLS certificate mounting, and protected ingress routing for operational surfaces.

## 3) What each mode includes

### Local/dev mode

Services included:

- mosquitto
- influxdb
- mongodb
- api
- worker
- simulator
- orchestration-adapter
- grafana
- nodered

Exposure characteristics:

- service ports are directly exposed for local iteration (`1883`, `8086`, `27017`, `8000`, `3000`, `1880`)
- direct local access does not represent production-like ingress protections

Primary use:

- development, troubleshooting, and local end-to-end verification

### Hosted baseline mode

Services included:

- mosquitto
- influxdb
- mongodb
- api
- worker

Exposure characteristics:

- core service ports are exposed by compose for hosted operation
- no nginx ingress boundary in this mode by default

Primary use:

- baseline hosted deployment of canonical ingestion/processing/API path

### Production-like ingress mode

Services included:

- mosquitto
- influxdb
- mongodb
- api
- worker
- simulator
- orchestration-adapter
- grafana
- nginx

Exposure characteristics:

- external ingress through nginx on ports `80` and `443`
- API runs behind nginx (API port is internal `expose`, not host-published)
- route and host-level access control is applied through nginx policy

Primary use:

- production-style topology validation with protected operational ingress behavior

## 4) Configuration model

Configuration is environment-variable driven.

### `.env` and environment variables

- hosted baseline and production-like compose files use `env_file: .env`
- use `infra/.env.example` as the configuration template
- do not commit real credentials or private tokens

### MongoDB configuration (`MONGO_URI`)

- API and worker operational persistence use `MONGO_URI`
- local MongoDB is used by default in compose stacks that include `mongodb`
- Atlas-backed persistence is supported by supplying an Atlas URI in `MONGO_URI`

### InfluxDB configuration

- worker requires `INFLUX_URL`, `INFLUX_ORG`, `INFLUX_BUCKET`, and `INFLUX_TOKEN`
- dev compose initializes InfluxDB with explicit setup variables in compose
- hosted and production-like deployment expect InfluxDB settings through `.env`

### Grafana/admin configuration

- dev compose sets Grafana admin credentials directly in compose for local use
- production-like compose loads Grafana credentials and settings from `.env`
- Grafana is an operational surface and should remain protected in hosted ingress deployments

### nginx, TLS, and basic-auth configuration

Production-like ingress expects:

- valid nginx config at `infra/nginx/nginx.conf`
- `.htpasswd` mounted for protected route access control
- TLS material mounted from host (`/etc/letsencrypt`) as configured in compose
- domain names, certificate paths, and auth credentials managed by the operator

## 5) Ingress and route exposure

In production-like mode, route exposure is defined by nginx policy.

### Public-safe route

- `GET /public-health` is exposed without basic auth
- this route is intentionally narrow and intended for health-style checks only
- perimeter controls should still constrain this path in internet-facing deployments (for example firewall allowlists, cloud load-balancer/CDN/WAF request controls, and narrow exposure policy)

### Protected operational API/dashboard routes

- operational API and dashboard routes behind `location /` are basic-auth protected
- acknowledgement route pattern is separately protected and write-rate limited (`limit_req zone=oncovax_write_limit burst=5 nodelay`; zone rate `3r/m` in `infra/nginx/nginx.conf`)

### Protected Grafana route

- Grafana host routing (`grafana.<domain>`) is basic-auth protected in nginx

### Environment note

- direct API access in local/dev or base hosted mode does not provide the same route protection model as nginx ingress mode

## 6) Hosted baseline guidance

Hosted baseline is implemented and supported as a practical operational deployment pattern.

Key properties:

- canonical MQTT -> worker -> InfluxDB + MongoDB/API path is preserved
- Atlas-backed operational persistence is supported through `MONGO_URI`
- domain, TLS certificate lifecycle, firewall scope, and credential policy are operator-managed

Hosted baseline should be treated as an operational reference baseline, not as a claim of full production hardening.

## 7) Operational validation

Use runbook-aligned checks after deployment and after operational changes.

### Core health and API checks

- `GET /health` for API liveness
- `GET /summary` for operational data availability
- `GET /alerts` for alert visibility checks

### Ingress checks (production-like)

- `GET /public-health` without auth through nginx
- authenticated `GET /summary` through nginx using basic-auth credentials

### Canonical command paths

- local verification: `make verify-local`
- smoke checks: `./scripts/smoke_test.sh`
- production-like smoke checks: `./scripts/smoke_test.sh --prod <domain> <username> <password>`

Detailed operational procedures are maintained in:

- `docs/RUNBOOK.md`
- `OPS_RUNBOOK.md`

## 8) Deployment limitations / non-claims

Current deployment support does not claim:

- telemetry from physical medical hardware fleets
- certified clinical or regulated infrastructure status
- fully hardened production infrastructure

Current limitations and dependencies:

- telemetry remains software-simulated in repository runtime
- deployment security and reliability depend strongly on operator-managed configuration quality
- ingress protections are meaningful in production-like mode, but application-layer auth/RBAC remains incomplete (see `SECURITY.md`)
- environment assumptions are not interchangeable across dev, hosted baseline, and production-like modes (see `docs/KNOWN_LIMITATIONS.md` and `docs/RUNBOOK.md`)
