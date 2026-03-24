# Evidence Map – OncoVax IoT Monitoring Platform

## Purpose

This document maps each platform capability to concrete implementation evidence (source files, API endpoints, and demo artifacts).

---

## Reviewer-first proof surfaces (Prompt G)

Use this section when evaluating the project as a portfolio/demo artifact.

### A) Product understanding proof

| Question | Evidence |
|---|---|
| What is this project? | `README.md`, `docs/OVERVIEW.md` |
| Why does it matter? | `docs/OVERVIEW.md` (cold-storage risk + monitoring workflow context) |
| How does the architecture work? | `docs/ARCHITECTURE.md`, `docs/DATA_FLOW.md` |

### B) Demo execution proof

| Question | Evidence |
|---|---|
| How do I run a guided end-to-end demo? | `docs/DEMO_WALKTHROUGH.md` |
| What scenarios should be shown? | `docs/DEMO_SCENARIOS.md`, `demo/scenarios.md` |
| What are the operational checks? | `docs/RUNBOOK.md`, `scripts/smoke_test.sh` |

### C) Observability proof

| Question | Evidence |
|---|---|
| Is telemetry visibly flowing? | `grafana/dashboards/oncovax-observability-final.v1.json` |
| How is Grafana configured/imported? | `grafana/README.md` |
| Is there screenshot evidence? | `demo/screenshots/README.md` (`sprint_11_*`, `sprint_12_*`) |

### D) Control-plane proof (D2)

| Question | Evidence |
|---|---|
| Are runtime-control commands documented and verifiable? | `docs/RUNBOOK.md` (D2 runtime-control section), `grafana/README.md` (expected panel behavior) |
| Are control artifacts present? | `flows/nodered/demo-control-flow.json`, `flows/nodered/README.md` |

### E) Cloud/live proof (Prompt E)

| Question | Evidence |
|---|---|
| Is hosted live routing documented/proven? | `docs/DEPLOYMENT.md`, `docs/RUNBOOK.md` production smoke section |
| Is live ingress behavior implemented and tested? | `infra/nginx/nginx.conf`, `tests/test_prompt_e_cloud_live_config.py` |
| Is hosted evidence visible? | `demo/screenshots/README.md` (`sprint_12_*`) |

### F) Safety/trust proof

| Question | Evidence |
|---|---|
| Are known boundaries and limitations explicit? | `docs/KNOWN_LIMITATIONS.md` |
| Are threat/security controls documented? | `docs/THREAT_MODEL.md`, `SECURITY.md` |
| Are rollback/recovery procedures present? | `docs/RECOVERY_AND_ROLLBACK.md` |

---

## Prompt H final closure proof surfaces

Use this section for final runtime/release verification closure.

| Prompt H question | Primary proof surface |
|---|---|
| What is the single reviewer entrypoint? | `README.md` |
| What is the canonical local zero-to-live-proof route? | `README.md` + `Makefile` target `verify-local` |
| Where is the explicit final validation/release gate? | `docs/FINAL_VALIDATION_CHECKLIST.md` |
| Where are observability and D2 reaction expectations defined? | `grafana/README.md`, `docs/RUNBOOK.md` |
| Where are cloud/live checks defined with truthful boundaries? | `README.md`, `docs/FINAL_VALIDATION_CHECKLIST.md`, `docs/RUNBOOK.md` |

---

## Capability Evidence

### 1. Telemetry Schema

| Item | Location |
|---|---|
| JSON schema definition | `schemas/telemetry.schema.json` |
| Worker validation code | `services/worker/worker.py` – `on_message()` (calls `jsonschema.validate`) |
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
| Worker InfluxDB write | `services/worker/worker.py` – `write_telemetry_point()` |
| InfluxDB container | `infra/docker-compose.dev.yml` – `influxdb` service |
| ADR | `docs/ADR/0002-influxdb.md` |

---

### 4. Excursion Alert Detection

| Item | Location |
|---|---|
| Threshold detection logic | `services/worker/worker.py` – `evaluate_excursion()` |
| Configurable threshold | `TEMP_THRESHOLD` env var (default: 8.0 °C) |
| Consecutive breach config | `CONSECUTIVE_BREACH_REQUIRED` env var |
| Alert InfluxDB write | `services/worker/worker.py` – `write_alert_point()` |

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
| Config constants | `services/api/config.py` |
| Pydantic models | `services/api/models.py` |
| `GET /health` | `services/api/routes/health.py` – `health()` |
| `GET /summary` | `services/api/routes/alerts.py` – `alert_summary()` |
| `GET /alerts` | `services/api/routes/alerts.py` – `list_alerts()` |
| `GET /alerts/{id}` | `services/api/routes/alerts.py` – `get_alert()` |
| `POST /alerts/{id}/acknowledge` | `services/api/routes/alerts.py` – `acknowledge_alert()` |
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

---

## Prompt G demo-review sequence

For recruiter/instructor review, use this exact order:

1. `README.md` (quick review entrypoint)
2. `docs/DEMO_WALKTHROUGH.md` (single narrative demo flow)
3. `docs/EVIDENCE_MAP.md` (this file) for claim-to-proof traceability
4. `demo/screenshots/README.md` for visual proof packs
5. `docs/RUNBOOK.md` production-like smoke command (`--prod`) when live verification is needed

## Prompt H final review sequence (closure)

1. `README.md` (single primary entrypoint + canonical local path)
2. `docs/FINAL_VALIDATION_CHECKLIST.md` (exact commands and expected outcomes)
3. `docs/EVIDENCE_MAP.md` (this file, claim-to-proof mapping)
4. `grafana/README.md` + dashboard JSON (observability/D2 behavior expectations)
5. `docs/RUNBOOK.md` + `./scripts/smoke_test.sh --prod ...` (real cloud/live execution path)
