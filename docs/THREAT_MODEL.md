# Threat Model

## 1) Threat model intent

This document defines a practical threat model for the OncoVax repository baseline.

It describes security-relevant boundaries, realistic threat categories, current mitigations, and known residual risks for the implemented architecture.

The model reflects a production-style hosted baseline and production-like ingress pattern, not fully hardened production assurance.

## 2) System boundaries

The current threat model covers these implemented system components and infrastructure contexts:

- simulator (`services/simulator/`)
- MQTT broker (Mosquitto)
- worker (`services/worker/`)
- InfluxDB (time-series store)
- MongoDB or Atlas-backed persistence (`MONGO_URI`)
- API service (`services/api/`)
- dashboard/UI (`services/web/` served by API)
- Grafana (`grafana/`)
- nginx ingress (`infra/nginx/nginx.conf` in production-like mode)
- live domain and external uptime monitoring as operator-managed infrastructure context

Scope notes:

- Telemetry in this repository runtime is software-simulated.
- The repository models a hosted operational baseline and ingress controls, with explicit maturity limits.

## 3) Trust boundaries

### 3.1 Public-safe route boundary

In production-like ingress mode, nginx exposes `GET /public-health` without basic auth as a narrow liveness route.

This path is intentionally limited and should not be treated as a complete security or correctness boundary by itself.

### 3.2 Protected operational surfaces

Current nginx policy protects operational routes through basic auth:

- `location /` (API/dashboard operational surface)
- acknowledgement route pattern `^/alerts/.*/acknowledge$`
- Grafana host routing

### 3.3 Ingress-layer protections vs app-layer limits

Current protection is primarily ingress-layer driven (TLS scaffolding, route segmentation, basic auth, selected rate limits).

Application-layer authentication/authorization (first-class API auth and RBAC) remains incomplete.

### 3.4 Persistence boundaries

- InfluxDB: telemetry and alert-series measurements.
- MongoDB/Atlas: operational lifecycle and audit records used by API workflows.

Risk posture depends on correct connectivity, credential handling, and exposure configuration for both stores.

## 4) Threat categories

### 4.1 Unauthorized ingress access

Threat:

- Unauthorized access attempts against protected API/dashboard and Grafana routes.

Potential impact:

- Unauthorized operational visibility or write actions if protections are bypassed or credentials are weak.

### 4.2 Credential exposure / weak secret hygiene

Threat:

- Exposure of `.env` credentials/tokens or weak credential rotation practices.

Potential impact:

- Unauthorized service/database access and lateral compromise of operational surfaces.

### 4.3 Misconfigured public exposure

Threat:

- Incorrect firewall/perimeter/domain/TLS configuration exposing routes or ports more broadly than intended.

Potential impact:

- Expanded attack surface, unauthorized probing, and higher abuse risk.

### 4.4 Telemetry/message tampering in deployment context

Threat:

- Unauthorized or untrusted publishers injecting or replaying MQTT messages in reachable network contexts.

Potential impact:

- False telemetry, misleading alert signals, operational confusion, and noisy incident handling.

### 4.5 Persistence/connectivity failures

Threat:

- MongoDB/Atlas or InfluxDB connectivity faults, credential mismatches, or degraded persistence availability.

Potential impact:

- Data loss windows, partial operational visibility, failed alert lifecycle operations, and unreliable summaries.

### 4.6 Observability blind spots / misleading health signals

Threat:

- Reliance on narrow liveness checks or dashboard snapshots without internal verification.

Potential impact:

- False confidence in system correctness while internal processing or persistence is degraded.

### 4.7 Operator error / configuration drift

Threat:

- Drift in compose, nginx, credentials, firewall rules, or domain/TLS configuration over time.

Potential impact:

- Security control regressions, availability incidents, or unintended public exposure.

## 5) Current mitigations

The repository currently provides these baseline mitigations:

- basic-auth protection for protected API/dashboard routes and Grafana (nginx policy)
- TLS scaffolding in production-like ingress path (certificate mounts and HTTPS routing)
- nginx rate limiting on selected protected/write paths:
  - general protected traffic (`oncovax_general_limit`)
  - acknowledgement write route (`oncovax_write_limit`)
- narrow public-safe route exposure (`/public-health`) rather than broad anonymous operational access
- documented restart/recovery procedures (deployment and runbook guidance)
- canonical operational verification path for post-change checks (`docs/RUNBOOK.md`)

These mitigations are useful baseline controls, not complete hardening.

## 6) Known residual risks

Residual risks that remain material:

- incomplete application-layer authentication/authorization and RBAC
- environment-file-based secret handling limitations compared to dedicated secrets systems
- dependence on operator-managed perimeter/domain/TLS/firewall correctness
- `public-health` reachability does not prove full internal service correctness
- observability stack is not a full enterprise detection/response platform
- environment-specific risk differences can create unsafe assumption carryover across dev/hosted/production-like modes

## 7) Environment differences

### 7.1 Local/dev risk posture (`infra/docker-compose.dev.yml`)

- broad direct port exposure for local iteration
- includes additional dev/demo surfaces
- hardcoded dev-oriented defaults exist in compose for local convenience
- unsuitable as-is for internet-facing deployment

### 7.2 Hosted baseline risk posture (`infra/docker-compose.yml`)

- core services exposed by compose without nginx ingress boundary by default
- operator controls (firewall/perimeter/credentials) are primary risk reducers
- supports Atlas-backed persistence with associated credential and network posture responsibilities

### 7.3 Production-like ingress risk posture (`infra/docker-compose.prod.yml` + nginx)

- adds ingress segmentation, TLS scaffolding, and basic-auth route protection
- includes selected nginx rate limits on protected/write paths
- still depends on strong operator execution (credential quality, firewall scope, TLS lifecycle, configuration discipline)
- improves baseline posture but does not eliminate residual risks listed above

## 8) Out-of-scope / non-claims

This threat model does not claim:

- physical medical device fleet threat coverage in repository runtime
- clinical/regulatory certification status
- complete production hardening or formal security assurance completion

This is a conservative, engineering-grade baseline threat model for current repository implementation and deployment patterns.
