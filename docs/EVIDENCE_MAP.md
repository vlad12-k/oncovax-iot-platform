# Evidence Map – OncoVax IoT Monitoring Platform

## Purpose

This document maps each platform capability to concrete implementation evidence (source files, API endpoints, and demo artifacts).

---

## Capability Evidence

### 1. Telemetry Schema

| Item | Location |
|---|---|
| JSON schema definition | `schemas/telemetry.schema.json` |
| Worker validation code | `services/worker/worker.py` – `validate_message()` |
| Simulator message structure | `services/simulator/simulator.py` – `make_reading()` |

---

### 2. MQTT Telemetry Pipeline

| Item | Location |
|---|---|
| Mosquitto broker config | `infra/mosquitto/mosquitto.conf` |
| Simulator MQTT publish | `services/simulator/simulator.py` – `client.publish()` |
| Worker MQTT subscribe | `services/worker/worker.py` – `on_message()` |
| Broker container config | `infra/docker-compose.dev.yml` – `mosquitto` service |

---

### 3. InfluxDB Time-Series Storage

| Item | Location |
|---|---|
| Worker InfluxDB write | `services/worker/worker.py` – `write_influx()` |
| InfluxDB container | `infra/docker-compose.dev.yml` – `influxdb` service |
| ADR | `docs/ADR/0002-influxdb.md` |

---

### 4. Excursion Alert Detection

| Item | Location |
|---|---|
| Threshold detection logic | `services/worker/worker.py` – `process_message()` |
| Configurable threshold | `TEMP_THRESHOLD` env var (default: 8.0 °C) |
| Consecutive breach config | `CONSECUTIVE_BREACH_REQUIRED` env var |
| Alert InfluxDB write | `services/worker/worker.py` – `write_alert_to_influx()` |

---

### 5. MongoDB Audit-Trail Records

| Item | Location |
|---|---|
| Audit record write | `services/worker/worker.py` – `write_audit_record()` |
| Audit schema (fields) | `alert_id`, `event_type`, `time`, `metric`, `value`, `device_id`, `asset_type`, `acknowledged`, `message` |
| MongoDB container | `infra/docker-compose.dev.yml` – `mongodb` service |
| ADR | `docs/ADR/0004-mongodb-audit.md` |

---

### 6. FastAPI REST API

| Item | Location |
|---|---|
| API entry point | `services/api/main.py` |
| `GET /health` | `services/api/main.py` – `health()` |
| `GET /summary` | `services/api/main.py` – `alert_summary()` |
| `GET /alerts` | `services/api/main.py` – `list_alerts()` |
| `GET /alerts/{id}` | `services/api/main.py` – `get_alert()` |
| `POST /alerts/{id}/acknowledge` | `services/api/main.py` – `acknowledge_alert()` |
| API container | `services/api/Dockerfile` |
| API requirements | `services/api/requirements.txt` |
| Postman collection | `tools/postman_collection.json` |

---

### 7. Operational Dashboard

| Item | Location |
|---|---|
| Dashboard HTML | `services/web/index.html` |
| Dashboard CSS | `services/web/styles.css` |
| Dashboard JS | `services/web/app.js` |
| Served by FastAPI | `services/api/main.py` – `FileResponse` + `StaticFiles` |
| Summary cards | `index.html` – `#total-alerts`, `#ack-alerts`, `#unack-alerts` |
| Alert table | `index.html` – `#alerts-body` |
| Filter/search | `app.js` – `filterEl`, `searchEl` |
| Acknowledgement from UI | `app.js` – `openAckModal()`, `submitAck()` |
| Alert detail panel | `app.js` – `openDetailPanel()` |

---

### 8. Acknowledgement Workflow

| Item | Location |
|---|---|
| Manual acknowledgement script | `services/tools/acknowledge_alert.py` |
| API acknowledge endpoint | `POST /alerts/{id}/acknowledge` |
| Worker acknowledgement fields | `acknowledged`, `acknowledged_by`, `acknowledged_at`, `incident_note` |
| UI acknowledgement modal | `services/web/app.js` |

---

### 9. MongoDB Atlas Integration

| Item | Location |
|---|---|
| Configuration | `MONGO_URI` env var (Atlas SRV string) |
| Documentation | `README.md` – Hosted baseline section |
| Worker compatibility | `pymongo` accepts Atlas URI transparently |
| API compatibility | Same – pymongo accepts Atlas URI |

---

### 10. Deployment Infrastructure

| Item | Location |
|---|---|
| Dev stack compose | `infra/docker-compose.dev.yml` |
| Base stack compose | `infra/docker-compose.yml` |
| Prod stack compose | `infra/docker-compose.prod.yml` |
| Nginx reverse proxy | `infra/nginx/nginx.conf` |
| Env example | `infra/.env.example` |
| Makefile | `Makefile` |

---

### 11. CI/CD and Quality Baseline

| Item | Location |
|---|---|
| CI sanity checks | `.github/workflows/ci.yml` |
| Docker build checks | `.github/workflows/docker-build.yml` |
| CodeQL scanning | `.github/workflows/codeql.yml` |
| Dependabot config | `.github/dependabot.yml` |
| Smoke test | `scripts/smoke_test.sh` |

---

### 12. Demo Evidence

| Sprint | Screenshot / Artefact | Location |
|---|---|---|
| Sprint 4 | Acknowledge alert script | `demo/screenshots/sprint_4_*` |
| Sprint 6 | Node-RED flow | `demo/screenshots/sprint_6_*` |
| Sprint 7 | API acknowledge POST | `demo/screenshots/sprint_7_*` |
| Sprint 8 | Containerised API health | `demo/screenshots/sprint_8_*` |
| Sprint 9 | Healthcheck configuration | `demo/screenshots/sprint_9_*` |
| Sprint 10 | API filtered alerts | `demo/screenshots/sprint_10_*` |
| Sprint 11 | Operational dashboard | `demo/screenshots/sprint_11_*` |
| Sprint 12 | Atlas + DigitalOcean | `demo/screenshots/sprint_12_*` |
| All | Scenario write-ups | `demo/scenarios.md` |
