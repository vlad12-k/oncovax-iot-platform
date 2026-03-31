# OncoVax Operator Quick Reference

## 1) Purpose

This file is a compact operator cheat sheet for routine verification, restart/recreate, and first-pass troubleshooting.

For complete procedures, environment-specific flow, and troubleshooting detail, use **`docs/RUNBOOK.md`**.

## 2) Core checks

### 2.1 Compose status

```bash
docker compose -f infra/docker-compose.prod.yml ps
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 2.2 Public-safe ingress check (`/public-health`)

```bash
curl -iS https://<live-domain>/public-health
```

Expected: HTTP 200 with `{"status":"ok"}`.

### 2.3 Internal API checks (`/health`, `/summary`, `/alerts`)

```bash
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/health").read().decode())'
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/summary").read().decode())'
docker exec oncovax-api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/alerts?limit=3").read().decode())'
```

## 3) Restart / recreate

### 3.1 Restart services

```bash
docker compose -f infra/docker-compose.prod.yml restart
docker compose -f infra/docker-compose.prod.yml ps
```

### 3.2 Force recreate containers

```bash
docker compose -f infra/docker-compose.prod.yml up -d --force-recreate
docker compose -f infra/docker-compose.prod.yml ps
```

## 4) Logs

```bash
docker logs --since=10m oncovax-nginx
docker logs --since=10m oncovax-api
docker logs --since=10m oncovax-worker
docker logs --since=10m oncovax-simulator
```

## 5) Interpretation reminders

- `/public-health` is a narrow liveness check, not full correctness validation.
- External uptime checks confirm reachability, not complete internal correctness.
- Protected operational surfaces must remain protected (auth-gated routes should still require valid credentials).

## 6) Rollback reminder

Rollback means restoring known-good configuration/artifacts, then revalidating compose status, API checks, ingress behavior, logs, and observability.

Primary rollback references:

- `docs/RECOVERY_AND_ROLLBACK.md`
- `docs/RUNBOOK.md`

## 7) Scope reminder

- This cheat sheet is for a production-style hosted baseline.
- Telemetry in repository runtime is software-simulated.
- This is not a certified clinical deployment runbook.
