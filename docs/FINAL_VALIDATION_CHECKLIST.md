# Final Validation Checklist (Prompt H Closure)

Use this checklist to determine whether OncoVax is truly review-ready and runtime-verifiable.

> Scope note: this checklist separates **locally provable** verification from **cloud/live environment** verification that requires real infrastructure.

---

## 0) Local prerequisites

- Docker Engine + Docker Compose installed
- `curl` available
- Access to local browser for API/Grafana views

---

## 1) Stack-up verification

### Command

```bash
make verify-local
```

### Expected outcome

- Dev compose containers are running (`mosquitto`, `influxdb`, `mongodb`, `oncovax-api`, `oncovax-worker`, `oncovax-simulator`, `oncovax-orchestration-adapter`, `grafana`)
- Smoke checks return healthy responses for Influx/API/Grafana and Mongo ping.

- [ ] Pass / [ ] Fail
- Evidence (terminal output / notes): ______________________________

---

## 2) Telemetry flow verification (simulator -> MQTT -> worker -> InfluxDB)

### Commands

```bash
docker compose -f infra/docker-compose.dev.yml logs --tail=60 worker
curl -s http://localhost:8000/summary | python -m json.tool
```

### Expected outcome

- Worker logs show continuous processing (no sustained connection/validation failure loop).
- API summary endpoint is reachable and returns valid JSON while simulator is running.

- [ ] Pass / [ ] Fail
- Evidence: ____________________________________________

---

## 3) Alert generation verification

### Commands

```bash
curl -s "http://localhost:8000/alerts?limit=20" | python -m json.tool
```

Optional forced pulse for faster demonstration:

```bash
docker exec mosquitto mosquitto_pub -t oncovax/demo/control/event/trigger \
  -m '{"command_id":"cmd-check-breach","issued_at":"2026-03-24T00:00:10Z","event_type":"breach_pulse","data":{"duration_cycles":3,"temperature_increase_c":9}}'
```

### Expected outcome

- Alerts endpoint returns records (or begins returning records shortly after breach pulse).
- Alert payload includes lifecycle/audit fields expected by API/dashboard flow.

- [ ] Pass / [ ] Fail
- Evidence: ____________________________________________

---

## 4) Mongo/audit visibility verification

### Command

```bash
docker exec mongodb mongosh oncovax --quiet \
  --eval 'db.audit_events.find({}).sort({time:-1}).limit(5).toArray()'
```

### Expected outcome

- Recent `audit_events` records are present and readable.

- [ ] Pass / [ ] Fail
- Evidence: ____________________________________________

---

## 5) Grafana population verification

### Commands / actions

1. Open `http://localhost:3000`
2. Import `grafana/dashboards/oncovax-observability-final.v1.json`
3. Use Influx datasource (URL `http://influxdb:8086`, org `oncovax`, bucket `telemetry`)
4. Set time range to include current simulator traffic

### Expected outcome

- Telemetry ingest panels update continuously
- Temperature/signal trend panels show active data
- Alert panels/table show breach activity when generated

- [ ] Pass / [ ] Fail
- Evidence (screenshot reference): _________________________________

---

## 6) D2 runtime-control reaction visibility verification

### Commands

In terminal A:

```bash
docker exec mosquitto mosquitto_sub -t oncovax/demo/orchestration/status -v
```

In terminal B (examples):

```bash
docker exec mosquitto mosquitto_pub -t oncovax/demo/control/scenario/select \
  -m '{"command_id":"cmd-h-s1","issued_at":"2026-03-24T00:01:00Z","scenario":"demo-friendly"}'
docker exec mosquitto mosquitto_pub -t oncovax/demo/control/mode/set \
  -m '{"command_id":"cmd-h-m1","issued_at":"2026-03-24T00:01:05Z","enabled":false}'
docker exec mosquitto mosquitto_pub -t oncovax/demo/control/event/trigger \
  -m '{"command_id":"cmd-h-e1","issued_at":"2026-03-24T00:01:10Z","event_type":"offline_pulse","data":{"duration_cycles":3}}'
docker exec mosquitto mosquitto_pub -t oncovax/demo/control/event/trigger \
  -m '{"command_id":"cmd-h-r1","issued_at":"2026-03-24T00:01:20Z","event_type":"reset_runtime"}'
```

### Expected outcome

- Status acknowledgements are visible on orchestration status topic.
- Corresponding trend shifts are visible in Grafana panels per `grafana/README.md`.

- [ ] Pass / [ ] Fail
- Evidence: ____________________________________________

---

## 7) Cloud/live verification path (requires real infrastructure)

### Command

```bash
./scripts/smoke_test.sh --prod oncovax.live oncovax-operator '<password>'
```

### Expected outcome

- `GET /public-health` returns via live domain without auth.
- `GET /summary` returns through nginx using valid credentials.

### Truthfulness boundary

- This step is **not locally provable** without real DNS/domain/TLS/credentials/network access.
- Passing this step requires real DigitalOcean/Atlas/domain execution context.

- [ ] Pass / [ ] Fail / [ ] Not executed in current environment
- Evidence: ____________________________________________

---

## 8) Prompt H definition of done (release gate)

Mark Prompt H complete only when:

- [ ] README is the single primary entrypoint with one canonical local route
- [ ] Local route verifies stack-up + telemetry + alerts + Mongo visibility + Grafana population + D2 effects
- [ ] Cloud/live path is documented truthfully (no fake guarantees)
- [ ] Evidence map links to final proof surfaces
- [ ] Guardrail tests for Prompt H artifacts pass

If any item above is unchecked, Prompt H is not complete.
