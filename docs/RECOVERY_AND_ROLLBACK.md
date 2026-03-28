# Recovery and Rollback

## 1) Document intent

This document defines the canonical recovery and rollback model for the OncoVax repository baseline.

It describes practical recovery actions, rollback scope, environment-specific differences, and required post-recovery validation.

This is baseline operational guidance for a production-style hosted architecture. It is not a claim of fully hardened production assurance.

## 2) Recovery principles

### 2.1 Restart first, diagnose second, recreate only when needed

Use the least disruptive action first:

1. check compose status and container health
2. review targeted logs for the failing layer
3. restart affected services
4. force-recreate only when restart does not restore service behavior

### 2.2 Service restart vs configuration rollback

- **Service restart** restarts running processes with current configuration and mounted artifacts.
- **Force recreate** replaces containers using current compose configuration and current mounted files.
- **Configuration rollback** restores previously known-good compose/nginx/env/dashboard artifacts.

Restart/recreate does not by itself revert bad configuration.

### 2.3 Layer-specific recovery domains

Treat recovery by boundary:

- **Ingress recovery**: nginx/TLS/basic-auth/routing behavior.
- **Application recovery**: API/worker/simulator service behavior.
- **Persistence recovery**: InfluxDB and MongoDB/Atlas data/connectivity state.

A successful action in one domain does not prove others are correct.

## 3) Rollback principles

### 3.1 What rollback means in this repository

Rollback means returning deployment configuration and runtime artifacts to a previously known-good state.

### 3.2 Typical rollback artifacts

Rollback may involve:

- compose configuration (`infra/docker-compose*.yml`)
- nginx configuration (`infra/nginx/nginx.conf`, auth file, TLS path wiring)
- dashboard/provisioning artifacts (`grafana/` provisioning and dashboard files)
- environment configuration (`infra/.env` and related operator-managed values)

### 3.3 Rollback limits

Rollback of configuration does not automatically restore:

- lost or corrupted persistence history
- all external managed-state changes
- all operator-side infrastructure changes made outside repository control

## 4) Environment differences

### 4.1 Local/dev (`infra/docker-compose.dev.yml`)

- broad direct service port exposure
- includes additional dev/demo tooling surfaces
- recovery is typically container-level and local-compose driven

### 4.2 Hosted baseline (`infra/docker-compose.yml`)

- core services only (no nginx ingress boundary by default)
- recovery centers on service health, API checks, worker flow, and persistence connectivity
- Atlas-backed persistence can be used via `MONGO_URI`

### 4.3 Production-like ingress (`infra/docker-compose.prod.yml` + nginx)

- includes nginx ingress, TLS wiring, protected operational routes, and Grafana
- recovery must validate both ingress behavior and internal API correctness
- public-safe route checks are required but are not sufficient for correctness

## 5) Typical recovery actions

### 5.1 Compose restart

Use restart for process-level recovery without changing current config:

```bash
docker compose -f infra/docker-compose.prod.yml restart
docker compose -f infra/docker-compose.prod.yml ps
```

### 5.2 Force recreate

Use recreate when restart is insufficient or container/image state is suspect:

```bash
docker compose -f infra/docker-compose.prod.yml up -d --force-recreate
docker compose -f infra/docker-compose.prod.yml ps
```

### 5.3 Targeted log review

Review logs by fault boundary (nginx/api/worker/simulator/persistence):

```bash
docker logs --since=10m oncovax-nginx
docker logs --since=10m oncovax-api
docker logs --since=10m oncovax-worker
docker logs --since=10m oncovax-simulator
```

### 5.4 API/internal checks

Validate internal API behavior after restart/recreate:

- `GET /health`
- `GET /summary`
- `GET /alerts`

### 5.5 Ingress/public-health validation

In production-like mode, validate:

- `GET /public-health` responds through nginx
- protected operational routes still require valid credentials

### 5.6 Observability sanity check

Use InfluxDB/Grafana views as sanity signals after recovery, then confirm with API and log checks.

## 6) Typical rollback scope

### 6.1 Compose configuration rollback

Restore previously known-good compose files and redeploy.

### 6.2 nginx configuration rollback

Restore known-good nginx route/auth/TLS configuration and reload via recreate/redeploy.

### 6.3 Dashboard/provisioning rollback

Restore known-good Grafana provisioning/dashboard artifacts when observability regressions are tied to dashboard/config changes.

### 6.4 Environment configuration rollback

Restore known-good `.env` values for service credentials, endpoints, and tokens.

### 6.5 Atlas-backed persistence dependency

When `MONGO_URI` points to Atlas, data/state behavior depends on external managed persistence posture.

Repository-side rollback can restore service configuration, but Atlas data restoration depends on operator-managed backup and restore capability.

## 7) Post-recovery validation

After restart, recreate, or rollback, run a full validation sequence.

### 7.1 Compose status and health

- `docker compose ... ps`
- container health status review for key services

### 7.2 API checks

- `GET /health`
- `GET /summary`
- `GET /alerts`

### 7.3 Public-safe ingress check

- `GET /public-health` through live ingress (production-like mode)

### 7.4 Protected-route behavior

- verify operational routes remain auth-protected

### 7.5 Log checks

- verify recent logs for ingress, API, worker, and simulator show no active failure loops

### 7.6 Observability checks

- verify telemetry/alert signals appear plausible in observability views
- cross-check with API outputs; do not rely on dashboards alone

### 7.7 Uptime-monitor interpretation

External uptime monitoring is an availability signal for public endpoint reachability.

It does not prove end-to-end correctness of worker processing, persistence state, or protected operational workflows.

## 8) Residual risks and limitations

- restart/recreate can restore process state but cannot guarantee correctness of all stored data
- rollback quality depends on disciplined capture of known-good configs and backup hygiene
- operator mistakes and configuration drift remain possible
- recovery still requires human judgment and verification
- this repository is not zero-touch recovery automation

## 9) Non-claims

This document is not:

- a disaster-recovery certification document
- a guarantee of complete data restoration
- an assurance artifact for clinical infrastructure recovery

It is a practical, canonical recovery/rollback baseline for the current repository architecture and deployment model.
