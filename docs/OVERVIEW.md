# Platform Overview – OncoVax IoT Monitoring Platform

## What This Platform Does

The OncoVax IoT Monitoring Platform is an event-driven telemetry pipeline and operational dashboard for regulated cold-storage monitoring.

It ingests simulated device telemetry over MQTT, validates and stores readings in InfluxDB, detects threshold excursions, and persists excursion alerts as durable audit records in MongoDB. Operators can review, filter, and acknowledge alerts through a lightweight web dashboard served by a FastAPI service.

---

## Core Capabilities

| Capability | Status | Notes |
|---|---|---|
| Telemetry ingestion via MQTT | ✅ Implemented | Simulator publishes; worker subscribes |
| Schema validation | ✅ Implemented | `telemetry.schema.json` validated by worker |
| InfluxDB time-series storage | ✅ Implemented | Telemetry and alerts stored in `telemetry` bucket |
| Threshold-based excursion detection | ✅ Implemented | `TEMP_THRESHOLD` env var |
| MongoDB audit-trail records | ✅ Implemented | `audit_events` collection |
| Alert acknowledgement workflow | ✅ Implemented | `POST /alerts/{id}/acknowledge` |
| REST API for alert management | ✅ Implemented | FastAPI, multiple endpoints |
| Operational dashboard | ✅ Implemented | HTML/CSS/JS, served by API container |
| Summary cards and alert table | ✅ Implemented | `/summary` + `/alerts` |
| Filter and search | ✅ Implemented | Client-side |
| Alert acknowledgement from UI | ✅ Implemented | Modal with `acknowledged_by` + `incident_note` |
| Grafana time-series views | ✅ Implemented (dev) | Requires InfluxDB data source setup |
| MongoDB Atlas integration | ✅ Implemented | Atlas URI via `MONGO_URI` env var |
| DigitalOcean hosted baseline | ✅ Implemented | Droplet + Atlas combination |
| Containerised deployment | ✅ Implemented | Docker Compose |
| CI/CD baseline | ✅ Implemented | GitHub Actions, CodeQL, Dependabot |

---

## What This Platform Is Not (Current Scope)

- Not a full production-hardened multi-tenant platform
- No user authentication or role-based access control (planned)
- No TLS termination from within the application layer (nginx provides this in prod)
- Not a regulatory submission package

---

## Data Flow

```
Simulator → MQTT → Worker → InfluxDB (time-series)
                          → MongoDB  (audit + acknowledgement)
                                  ↑
                             FastAPI REST API
                                  ↑
                         Operational Dashboard
```

---

## Platform Stack

| Layer | Technology |
|---|---|
| Message broker | Mosquitto MQTT |
| Telemetry simulator | Python + paho-mqtt |
| Worker | Python + paho-mqtt + influxdb-client + pymongo |
| Time-series DB | InfluxDB 2.7 |
| Audit/workflow DB | MongoDB 7 / MongoDB Atlas |
| API | FastAPI + uvicorn + pymongo |
| Dashboard | HTML + CSS + JavaScript |
| Visualisation | Grafana |
| Containerisation | Docker Compose |
| Cloud database | MongoDB Atlas |
| Hosted runtime | DigitalOcean Droplet |
| CI quality | GitHub Actions + CodeQL + Dependabot |

---

## Repository Structure

```
infra/                  Docker Compose configs, mosquitto config, env example
services/
  simulator/            Telemetry publisher
  worker/               Telemetry consumer, excursion detection, persistence
  api/                  FastAPI service + Dockerfile
  web/                  Dashboard frontend (HTML/CSS/JS)
  tools/                Operational utility scripts
schemas/                JSON schema for telemetry validation
docs/                   Architecture, runbook, threat model, deployment docs
scripts/                Smoke test and utility scripts
tests/                  Test assets
demo/                   Screenshots and scenario write-ups
tools/                  Postman collection
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical architecture.
