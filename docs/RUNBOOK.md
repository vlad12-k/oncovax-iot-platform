# Operations Runbook

## 1) Runbook intent

This document defines the canonical operational verification and recovery-oriented check path for the OncoVax repository baseline.

It is intended to help operators validate service health, ingress behavior, telemetry/alert flow visibility, and post-change operational state across supported deployment modes.

This runbook represents practical baseline operations guidance, not a claim of fully hardened production operations.

## 2) Core verification checks

Use these checks in order after startup, restart, configuration changes, or incident response.

### 2.1 Compose service status

Local/dev:

```bash
docker compose -f infra/docker-compose.dev.yml ps
```

Hosted baseline:

```bash
docker compose -f infra/docker-compose.yml ps
```

Production-like ingress:

```bash
docker compose -f infra/docker-compose.prod.yml ps
```

### 2.2 Container health state

Inspect health for services that declare health checks in compose (for example API, worker, nginx, simulator, orchestration adapter, and Grafana where applicable):

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

If any service is restarting or unhealthy, inspect logs before continuing with API/ingress validation.

### 2.3 Public-safe ingress check (`/public-health`)

In production-like ingress mode, validate public-safe route behavior through nginx:

```bash
curl -iS https://<live-domain>/public-health
```

Expected behavior:

- HTTP 200
- JSON body includes `{"status":"ok"}`

### 2.4 Internal API checks (`/health`, `/summary`, `/alerts`)

Local/dev or hosted baseline direct checks:

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8000/summary | python -m json.tool
curl -s "http://localhost:8000/alerts?limit=20" | python -m json.tool
```

Production-like internal checks from API container:

```bash
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/health").read().decode())'
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/summary").read().decode())'
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/alerts?limit=3").read().decode())'
```

### 2.5 Log inspection paths

Local/dev logs:

```bash
docker compose -f infra/docker-compose.dev.yml logs -f --tail=200
```

Production-like targeted logs:

```bash
docker logs --since=10m oncovax-nginx
docker logs --since=10m oncovax-api
docker logs --since=10m oncovax-worker
docker logs --since=10m oncovax-simulator
```

## 3) Environment-specific runbook behavior

### 3.1 Local/dev (`infra/docker-compose.dev.yml`)

- Includes full local stack (including Grafana and Node-RED).
- Uses direct local port exposure for operational checks.
- Best for local end-to-end validation and troubleshooting.

Canonical local verification entrypoint:

```bash
make verify-local
```

### 3.2 Hosted baseline (`infra/docker-compose.yml`)

- Includes core services (mosquitto, worker, API, InfluxDB, MongoDB).
- No nginx ingress boundary in this mode by default.
- Grafana is not included by default in this compose mode.
- Operational validation relies on compose status, API checks, and logs.

### 3.3 Production-like ingress (`infra/docker-compose.prod.yml` + nginx)

- Includes nginx ingress with TLS/basic-auth route controls.
- Includes Grafana and orchestration adapter.
- Uses public-safe ingress checks plus authenticated/protected operational checks.

Canonical production-like smoke command:

```bash
./scripts/smoke_test.sh --prod <domain> <username> <password>
```

## 4) Ingress and domain checks

The hosted baseline can use a live custom domain managed by operators.

### 4.1 Public-safe route behavior

- `GET /public-health` is intentionally exposed for narrow liveness checks.
- This route is not a complete operational correctness check.

### 4.2 Protected operational surfaces

In production-like ingress policy:

- Operational API/dashboard routes behind `location /` are protected by basic auth.
- Alert acknowledgement routes are protected and write-rate limited.
- Grafana host routing is protected by basic auth.

### 4.3 Ingress validation sequence

1. Confirm domain resolves and TLS ingress responds.
2. Confirm `/public-health` returns expected liveness response.
3. Confirm protected operational routes require valid credentials.
4. Confirm internal API checks still pass.

## 5) Monitoring interpretation

External uptime monitoring is useful for detecting public endpoint availability changes.

What it indicates:

- external reachability of the public-safe endpoint
- whether ingress liveness responses are available

What it does not prove:

- full correctness of API workflows, worker processing, or persistence state
- correctness of protected route behavior without authenticated checks
- full internal health across all services and dependencies

Always pair uptime-monitor observations with API/internal checks and service-log review.

## 6) Operational troubleshooting categories

### 6.1 Ingress problems

Symptoms:

- `/public-health` unavailable or non-200
- TLS errors or repeated redirect/auth failures

Checks:

- `docker logs --since=10m oncovax-nginx`
- nginx container status and health
- TLS material mount and domain alignment with nginx configuration

### 6.2 API problems

Symptoms:

- `/health` fails
- `/summary` or `/alerts` returns errors or empty/unexpected data

Checks:

- API container logs
- API container health status
- API-to-MongoDB connectivity (`MONGO_URI` correctness)

### 6.3 Worker / telemetry-flow problems

Symptoms:

- missing telemetry progression
- missing alert generation despite expected threshold conditions

Checks:

- worker logs for MQTT subscription, parse, and write errors
- MQTT broker/container status
- worker environment settings (`MQTT_TOPIC`, InfluxDB variables, threshold settings)

### 6.4 Observability / Grafana visibility problems

Symptoms:

- dashboards show no data despite active services

Checks:

- InfluxDB health and write activity
- Grafana container health (production-like or dev where present)
- dashboard time-window selection and data-source mapping

Interpretation rule:

- “No data” can reflect time-window/data-state issues, not only service failure.

### 6.5 Persistence problems

Symptoms:

- API operational reads fail
- acknowledgements fail or do not persist

Checks:

- MongoDB service status and logs
- `MONGO_URI` configuration (including Atlas-backed configuration where used)
- API and worker connectivity to persistence endpoints

## 7) Operator responsibilities

Operators remain responsible for deployment safety and correctness, including:

- credential management (basic-auth, service credentials, token rotation)
- TLS certificate and live domain configuration lifecycle
- firewall/perimeter exposure policy
- secret hygiene (`.env`/runtime-secret handling, no committed real secrets)
- validation discipline after restarts, config changes, or incident recovery

Recommended post-change discipline:

1. Compose status and health verification
2. Public-safe ingress verification
3. Internal API verification
4. Log review for ingress/API/worker errors
5. Observability-layer sanity check (InfluxDB/Grafana where applicable)

## 8) Recovery and restart references

### 8.1 Standard restart

Local/dev:

```bash
docker compose -f infra/docker-compose.dev.yml restart
docker compose -f infra/docker-compose.dev.yml ps
```

Production-like:

```bash
docker compose -f infra/docker-compose.prod.yml restart
docker compose -f infra/docker-compose.prod.yml ps
```

### 8.2 Force recreate (production-like)

```bash
docker compose -f infra/docker-compose.prod.yml up -d --force-recreate
docker compose -f infra/docker-compose.prod.yml ps
```

After restart/recreate, rerun the core verification checks in Section 2.

## 9) Non-claims

This runbook does not claim:

- zero-touch autonomous operations
- fully hardened production operations
- clinical infrastructure operations certification

The repository runbook is an operator-driven baseline for production-style operations with explicit scope and maturity limits.
