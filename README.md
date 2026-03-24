# OncoVax IoT Monitoring Platform

OncoVax is an event-driven monitoring stack for cold-storage telemetry: it ingests device/simulator telemetry over MQTT, validates and processes it in a worker, stores time-series in InfluxDB, stores alert/audit records in MongoDB, serves operational APIs and dashboard via FastAPI, and supports observability and runtime-control verification in dev.

This README is the **single primary entrypoint** for review and runtime verification.

---

## Recruiter / instructor quick review (10–15 minutes)

1. Start with this README and execute the canonical local route in section **Zero-to-live-proof local route (Prompt H canonical path)**.
2. Follow [docs/DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md) for a narrative demo sequence.
3. Use [docs/EVIDENCE_MAP.md](docs/EVIDENCE_MAP.md) for claim-to-proof mapping.
4. Browse [demo/screenshots/README.md](demo/screenshots/README.md) for visual evidence.

---

## 1) What this product is

- **Problem:** cold-storage excursions must be detected quickly and audited.
- **System:** simulator/device telemetry -> MQTT -> worker -> InfluxDB + MongoDB -> API/dashboard + Grafana.
- **Operator workflow:** view alerts, filter/search, acknowledge incidents with audit fields.

Architecture summary:

```text
Simulator -> MQTT -> Worker -> InfluxDB (telemetry + alert series)
                           -> MongoDB (audit_events lifecycle)
                                     ^
                                   FastAPI
                                     ^
                                Web dashboard
                                     +
                                  Grafana
```

---

## 2) What is already automated

- Dockerized local/dev stack via `infra/docker-compose.dev.yml`
- Baseline smoke checks via `./scripts/smoke_test.sh`
- Canonical local runtime entrypoint via `make verify-local`
- Prompt guardrail tests in `tests/`

---

## 3) Zero-to-live-proof local route (Prompt H canonical path)

Use this as the primary reviewer path.

### Step A — Bring stack up with one command path

```bash
make verify-local
```

This runs:

- `docker compose -f infra/docker-compose.dev.yml up -d --build`
- `./scripts/smoke_test.sh`

### Step B — Verify telemetry + alerts at API surface

```bash
curl -s http://localhost:8000/summary | python -m json.tool
curl -s "http://localhost:8000/alerts?limit=20" | python -m json.tool
```

Expected: non-error JSON responses, with alert counts/events increasing while simulator runs.

### Step C — Verify Mongo audit visibility

```bash
docker exec mongodb mongosh oncovax --quiet \
  --eval 'db.audit_events.find({}).sort({time:-1}).limit(5).toArray()'
```

Expected: recent audit/alert lifecycle records exist.

### Step D — Verify Grafana population

1. Open `http://localhost:3000` (admin/adminadminadmin in dev compose).
2. Import dashboard: `grafana/dashboards/oncovax-observability-final.v1.json`.
3. Map datasource input to InfluxDB datasource (`http://influxdb:8086`, org `oncovax`, bucket `telemetry`).
4. Set time range to include active simulator traffic.

Expected: ingest and trend panels update, alert panels populate when breaches occur.

### Step E — Verify D2 runtime-control visibility

Run status subscriber:

```bash
docker exec mosquitto mosquitto_sub -t oncovax/demo/orchestration/status -v
```

Trigger control events from another terminal:

```bash
docker exec mosquitto mosquitto_pub -t oncovax/demo/control/event/trigger \
  -m '{"command_id":"cmd-h-breach","issued_at":"2026-03-24T00:00:00Z","event_type":"breach_pulse","data":{"duration_cycles":3,"temperature_increase_c":9}}'
```

Expected: orchestration status messages appear, and Grafana trend/alert behavior visibly reacts (per `grafana/README.md` D2 expectations).

---

## 4) Cloud/live verification path (truthful boundary)

Cloud/live verification is documented and partially automated, but requires real infrastructure and credentials.

Production-like smoke path:

```bash
./scripts/smoke_test.sh --prod oncovax.live oncovax-operator '<password>'
```

This verifies:

- unauthenticated `GET /public-health`
- authenticated `GET /summary` through nginx

### What is proven locally vs requires real cloud execution

- **Proven locally in this repo path:** dev compose startup, simulator/worker ingest path, API/dashboard behavior, Mongo audit visibility, Grafana population, D2 reaction path.
- **Requires real DigitalOcean/Atlas/domain execution:** external DNS, TLS cert wiring, internet-facing nginx routing, hosted credentials/network policy, live uptime from outside local environment.

---

## 5) Final validation and definition of done

Use:

- `docs/FINAL_VALIDATION_CHECKLIST.md` (Prompt H release/verification checklist)

Prompt H is considered done only when every required checklist item passes with observed evidence.

---

## 6) Evidence links

- Final checklist: `docs/FINAL_VALIDATION_CHECKLIST.md`
- Evidence map: `docs/EVIDENCE_MAP.md`
- Runbook details: `docs/RUNBOOK.md`
- Grafana import/visibility details: `grafana/README.md`
- Demo walkthrough: `docs/DEMO_WALKTHROUGH.md`
- Known limitations: `docs/KNOWN_LIMITATIONS.md`

---

## 7) Limitations and truthfulness

- This repository is a **production-like baseline**, not a fully hardened production platform.
- No live secrets are stored in-repo.
- Do not claim cloud/live guarantees unless executed against real infrastructure.
- Node-RED remains dev/demo-only and is not the canonical ingestion authority in production path.
