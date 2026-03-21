# Observability – OncoVax IoT Monitoring Platform

## Overview

This document describes the current observability baseline for the OncoVax IoT Monitoring Platform. It covers logging, health checking, metrics visibility, and alert monitoring.

---

## Health Checks

### API Service

The FastAPI service exposes a health endpoint:

```
GET /health
→ {"status": "ok"}
```

The Docker Compose healthcheck configuration polls this endpoint every 30 seconds:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 10s
```

### InfluxDB

InfluxDB exposes its own health endpoint:

```
GET http://localhost:8086/health
→ {"name":"influxdb","message":"ready for queries and writes","status":"pass",...}
```

### Smoke Test

A smoke test script is provided at `scripts/smoke_test.sh`. It checks:
- Docker container running state
- InfluxDB health endpoint
- Grafana login page availability
- API health endpoint
- MongoDB container reachability

Run it after deployment:

```bash
./scripts/smoke_test.sh
```

---

## Logging

### API Service

The FastAPI service logs are emitted to stdout by uvicorn and captured by Docker. To view:

```bash
docker compose logs -f api
```

Default uvicorn log format includes request method, path, status code, and response time.

### Worker Service

The worker logs:
- MQTT connection events
- Each received telemetry message (device_id, metric, value)
- Schema validation failures
- Threshold breaches detected
- InfluxDB write confirmations
- MongoDB write confirmations

```bash
docker compose logs -f worker
```

### Simulator

The simulator logs each published message to stdout.

```bash
docker compose logs -f simulator
```

---

## Metrics and Time-Series Visibility

### InfluxDB

All telemetry and alert records are stored in InfluxDB under the `telemetry` bucket:
- Measurement: `telemetry` – raw device readings (device_id, metric, value, unit)
- Measurement: `alerts` – threshold breach events

Access the InfluxDB UI at `http://localhost:8086` (dev) to explore data with the built-in Data Explorer.

### Grafana

Grafana (dev stack only) is configured at `http://localhost:3000`.

To view telemetry:
1. Add InfluxDB as a data source (URL: `http://influxdb:8086`, token from `.env`)
2. Create panels to visualise temperature readings and alert markers

Note: Grafana panels will show **No data** if no telemetry has been produced in the selected time window. This reflects the data state, not a system failure.

---

## Alert Monitoring

Excursion alerts are visible through:

1. **Operational Dashboard** at `http://localhost:8000`
   - Summary cards (total / acknowledged / unacknowledged)
   - Alert table with filter and search
   - Acknowledgement workflow via modal

2. **API endpoints** (for programmatic access):
   - `GET /summary` – counts by acknowledgement state
   - `GET /alerts` – list with optional filter
   - `GET /alerts/{id}` – individual alert detail

---

## Current Limitations

- No centralised log aggregation (e.g., no ELK or Loki stack)
- No alerting on service downtime (no uptime monitor or pager)
- Health check at `/health` does not yet verify MongoDB reachability
- No distributed tracing
- No Prometheus metrics endpoint

These are appropriate for the current MVP and hosted baseline scope. Production hardening would require expanding this layer.
