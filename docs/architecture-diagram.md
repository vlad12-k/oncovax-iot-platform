# OncoVax Architecture Diagram

## 1) Diagram intent

This diagram is the canonical architecture view for the OncoVax hosted baseline.

It shows:

- software-simulated telemetry ingestion
- event processing and persistence boundaries
- production-like ingress routing boundaries
- public-safe versus protected operational surfaces
- hosted server/cloud VM deployment context
- external uptime checks as availability-signal context

It does not claim full production hardening or certified clinical infrastructure.

## 2) Canonical diagram asset (GitHub-rendered)

![OncoVax Architecture Diagram](./assets/oncovax-architecture-diagram.svg)

If the image does not render in your context, open the raw asset directly:

- `docs/assets/oncovax-architecture-diagram.svg`

## 3) Topology interpretation

### Hosted baseline boundary

The hosted baseline runs on a cloud VM/server boundary that contains ingress, application services, and core runtime dependencies.

### Ingestion and processing pipeline

1. Software simulator(s) publish telemetry to Mosquitto (MQTT).
2. Worker subscribes, validates payloads, and evaluates thresholds.
3. Worker writes telemetry/alert-series data to InfluxDB.
4. Worker writes alert lifecycle/audit records to MongoDB.

### Persistence roles

- **InfluxDB**: time-series telemetry and alert signals.
- **MongoDB (Atlas-backed via `MONGO_URI` when configured)**: operational lifecycle/audit persistence boundary.

### API and observability roles

- **FastAPI/dashboard layer**: operational endpoints and dashboard experience.
- **Grafana**: observability views backed by InfluxDB.

### Ingress and exposure boundaries

- **Live domain ingress boundary** is enforced by nginx.
- **Public-safe surface** is limited to `GET /public-health`.
- **Protected operational surfaces** include operational API/dashboard paths and Grafana host routing.

### Uptime signal boundary

External uptime monitoring checks public endpoint reachability and liveness behavior. It is an availability signal, not proof of full internal correctness.

## 4) Non-claims

This architecture view does **not** claim:

- physical medical device telemetry ingestion in repository runtime
- certified clinical or regulated deployment status
- complete production hardening or complete security assurance

## 5) Related canonical references

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_FLOW.md`
- `docs/DEPLOYMENT.md`
- `docs/OBSERVABILITY.md`
- `SECURITY.md`
- `docs/EVIDENCE_MAP.md`
