# Architecture Overview – OncoVax IoT Monitoring Platform

## Purpose

This document describes the technical architecture of the OncoVax IoT Monitoring Platform: an event-driven pipeline for cold-storage telemetry ingestion, threshold-based excursion detection, audit-trail management, and operator alerting.

---

## System Diagram

```
Simulator
   │
   │  MQTT (paho)  topic: oncovax/telemetry
   ▼
Mosquitto MQTT Broker  (eclipse-mosquitto:2)
   │
   │  subscribe
   ▼
Worker Service  (Python)
   ├─── schema validation (telemetry.schema.json)
   ├─── threshold check  (TEMP_THRESHOLD env var)
   ├─── [on breach] ──► InfluxDB  (alert measurement)
   └─── [on breach] ──► MongoDB   (audit_events collection)
                           │
                           │  pymongo
                           ▼
                      FastAPI Service  (:8000)
                           │
                           ├─ GET  /health
                           ├─ GET  /summary
                           ├─ GET  /alerts
                           ├─ GET  /alerts/{alert_id}
                           ├─ POST /alerts/{alert_id}/acknowledge
                           └─ GET  /           → serves dashboard (index.html)
                                    │
                                    ▼
                           Operational Dashboard  (HTML/CSS/JS)
                           services/web/index.html + styles.css + app.js

InfluxDB (:8086)
   └─── telemetry + alert time-series
   └─── Grafana (:3000) – time-series visualisation

MongoDB / MongoDB Atlas
   └─── audit_events collection
        Fields: alert_id, event_type, time, metric, value, device_id,
                asset_type, acknowledged, acknowledged_by, acknowledged_at,
                incident_note, message
```

---

## Services

### Simulator (`services/simulator/`)

- Language: Python
- Publishes cold-storage telemetry readings to MQTT
- Message schema: `schemas/telemetry.schema.json`
- Injects occasional excursion spikes (demo mode)
- Configurable via environment: `MQTT_HOST`, `MQTT_PORT`, `MQTT_TOPIC`, `DEVICE_ID`, `ASSET_TYPE`

### Worker (`services/worker/`)

- Language: Python
- Subscribes to `oncovax/telemetry` MQTT topic
- Validates each message against `telemetry.schema.json` using `jsonschema`
- Writes all valid telemetry to InfluxDB (`telemetry` bucket)
- Detects threshold breaches (temperature > `TEMP_THRESHOLD`)
- On breach:
  - Writes alert record to InfluxDB (`alerts` measurement)
  - Writes audit document to MongoDB `audit_events` collection
- Configurable via environment: `MQTT_*`, `INFLUX_*`, `MONGO_*`, `TEMP_THRESHOLD`

### API (`services/api/`)

- Language: Python, FastAPI
- Serves operational dashboard at `GET /`
- Provides REST API for alert retrieval and acknowledgement (routes in `services/api/routes/`)
- Reads from MongoDB `audit_events` collection via `pymongo`
- Configuration via environment variables:
  - `MONGO_URI`, `MONGO_DB`, `MONGO_COLLECTION`
  - `CORS_ALLOWED_ORIGINS` (comma-separated allowlist; default is same-origin only)
- Dockerised; health check at `GET /health`

### Dashboard (`services/web/`)

- Plain HTML/CSS/JavaScript (no frontend framework)
- Served directly by the FastAPI container via `FileResponse` and `StaticFiles`
- Communicates with the API via same-origin `fetch()` calls
- Files: `index.html`, `styles.css`, `app.js`

### Node-RED demo orchestration (`flows/nodered/`)

- Scope: **dev/demo-only** optional orchestration artifact layer
- Export artifact: `flows/nodered/demo-control-flow.json`
- Approved control topics:
  - `oncovax/demo/control/scenario/select`
  - `oncovax/demo/control/mode/set`
  - `oncovax/demo/control/event/trigger`
- Approved status topic:
  - `oncovax/demo/orchestration/status`
- Purpose: receive demo control commands, validate basic shape, emit orchestration status
- Non-goal: Node-RED is not required for ingestion correctness and does not replace direct worker ingestion

### D2 runtime control mapping (dev/demo-only)

An additive orchestration adapter service subscribes to the same approved demo-control topics and maps accepted commands to the simulator's internal runtime-control topic:

- Internal runtime-control topic:
  - `oncovax/demo/internal/simulator/runtime/control`
- Locked `event_type` values:
  - `burst_pulse`
  - `breach_pulse`
  - `offline_pulse`
  - `reset_runtime`

Runtime semantics:

- `scenario/select` → persistent simulator scenario change
- `mode/set` (`enabled=true|false`) → persistent simulator profile change (`demo`/`standard`)
- `burst_pulse` / `breach_pulse` / `offline_pulse` → temporary override for `duration_cycles` with automatic expiry
- `reset_runtime` → clear temporary overrides and restore startup scenario/profile defaults

---

## Data Layers

### InfluxDB

- Role: time-series telemetry and alert storage
- Measurements: `telemetry`, `alerts`
- Retention: default (configurable via InfluxDB admin)
- Visualisation: Grafana dashboards

### MongoDB / MongoDB Atlas

- Role: durable audit trail and operational alert workflow
- Collection: `audit_events`
- Supports: acknowledgement state, acknowledged_by, incident_note
- Atlas: used for hosted baseline (cloud-managed)

---

## Network and Ports (dev)

| Service   | Port  | Notes                         |
|-----------|-------|-------------------------------|
| Mosquitto | 1883  | MQTT broker                   |
| InfluxDB  | 8086  | Time-series DB + UI           |
| MongoDB   | 27017 | Local dev only (Atlas in prod)|
| FastAPI   | 8000  | API + dashboard                |
| Grafana   | 3000  | Visualisation (dev only)      |
| Node-RED  | 1880  | Demo-control flow editor/runtime (dev/demo only) |

---

## Configuration and Secrets

- All sensitive values are injected via environment variables
- `.env.example` files document required variables; never commit real `.env` files
- Docker Compose uses `env_file: .env` for service configuration

---

## Deployment Targets

- **Local dev**: `docker compose -f infra/docker-compose.dev.yml up -d`
- **Hosted baseline**: DigitalOcean Droplet + MongoDB Atlas
- **Production-like**: see `infra/docker-compose.prod.yml` + `infra/nginx/`

Authoritative ingestion path remains direct MQTT telemetry to worker. Optional Node-RED demo orchestration uses `oncovax/demo/**` topics only and does not alter worker ingestion wiring.

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment instructions.


---

## Phase B2c Demo-Control Orchestration Boundary

Node-RED is an optional **dev/demo-only** orchestration surface for demo control topics.

- Control topics:
  - `oncovax/demo/control/scenario/select`
  - `oncovax/demo/control/mode/set`
  - `oncovax/demo/control/event/trigger`
- Status topic:
  - `oncovax/demo/orchestration/status`

The exported flow artifact is `flows/nodered/demo-control-flow.json`.
It validates basic command shape and emits orchestration status events on the demo status topic.

This does **not** change ingestion authority:

- Authoritative ingestion path remains direct `MQTT -> worker`.
- Worker validation and persistence logic remain unchanged.
- No runtime rewiring to make Node-RED mandatory for ingestion correctness.

---

## Phase A Repository Completion Artifacts

The following additive repository structures are intentionally introduced to support future operational exports without changing runtime behavior:

- `flows/` and `flows/nodered/` for Node-RED flow exports
- `grafana/dashboards/` for Grafana dashboard JSON exports
- `services/simulator/scenarios/` for scenario templates
- `schemas/alert.schema.json`, `schemas/audit_event.schema.json`, `schemas/device_metadata.schema.json` as contract placeholders

These artifacts are documentation and structure scaffolding only for this phase.
