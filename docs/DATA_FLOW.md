# Data Flow

## 1) Purpose

This document defines the canonical data-flow model for the OncoVax platform baseline. It describes how telemetry, alerts, and operational records move through the implemented services and storage boundaries.

## 2) Telemetry ingestion flow

1. The simulator (`services/simulator/`) generates software telemetry events.
2. Telemetry is published to Mosquitto over MQTT.
3. The worker (`services/worker/`) subscribes to telemetry topics and validates incoming payloads.
4. Valid telemetry is written by the worker to InfluxDB time-series storage.

Notes:

- In local/dev compose, simulator telemetry is published on `oncovax/telemetry/simulator` to support development and demo runtime behavior.
- Worker handles this with a compatibility subscription (`MQTT_SIMULATOR_COMPAT_TOPIC`) in addition to the canonical telemetry subscription.
- In hosted baseline and production-like deployment, canonical telemetry topic configuration is `oncovax/telemetry` via environment settings (`MQTT_TOPIC`).
- Canonical ingestion authority remains MQTT transport into worker processing.

## 3) Alert generation flow

1. Worker evaluates telemetry against configured threshold logic.
2. When threshold conditions are met, worker writes alert-series data to InfluxDB.
3. Worker writes alert lifecycle and operational audit records to MongoDB (`audit_events`).

This separates time-series alert signal visibility from operational alert workflow state.

## 4) Operational API flow

1. API service (`services/api/`) reads operational records from MongoDB.
2. API serves health and operational endpoints, including summary, alert list/detail, and acknowledgement behavior.
3. Dashboard/UI (`services/web/`) consumes API-facing operational data for operator workflows.

In production-like topology, these operational surfaces are served behind nginx route protection.

## 5) Observability flow

1. Grafana queries InfluxDB for telemetry and alert-series visualization.
2. Observability dashboards depend on InfluxDB time-series data.
3. MongoDB operational records are not the primary Grafana dashboard source.

In production-like topology, Grafana is a protected operational surface behind nginx basic-auth host routing.

## 6) Persistence boundaries

### InfluxDB boundary

InfluxDB stores:

- telemetry measurements
- alert-series measurements used for trend and dashboard visualization

### MongoDB boundary

MongoDB stores:

- alert lifecycle and acknowledgement state
- operational/audit event records supporting API workflows

### Atlas-backed hosted baseline compatibility

Hosted baseline supports Atlas-backed operational persistence through `MONGO_URI` configuration, preserving the same API-facing operational record model.

## 7) Runtime/control path (implemented)

The repository includes an orchestration adapter (`services/orchestration_adapter/`) that handles demo/runtime-control MQTT topics and publishes simulator runtime-control events.

This path is additive:

- it supports runtime/demo-control behavior
- it does not replace canonical telemetry ingestion (`simulator -> MQTT -> worker`)

## 8) Environment notes

### Local/dev (`infra/docker-compose.dev.yml`)

- Includes simulator, Mosquitto, worker, API/UI, InfluxDB, MongoDB, Grafana, Node-RED, and orchestration adapter.
- Exposes development ports directly for local testing.

### Hosted baseline (`infra/docker-compose.yml`)

- Core hosted stack for Mosquitto, worker, API, InfluxDB, and MongoDB.
- Data-flow logic remains the same across MQTT ingestion, worker processing, and split persistence boundaries.

### Production-like ingress path (`infra/docker-compose.prod.yml` + `infra/nginx/nginx.conf`)

- Keeps the same processing and persistence flow.
- Changes exposure model through nginx TLS routing and protected operational surfaces.
- Exposes a narrow public-safe route (`/public-health`) and protects operational API/UI and Grafana boundaries.

## 9) Out-of-scope / non-claims

This data-flow model does not claim:

- telemetry from a physical device fleet as represented by this repository runtime
- certified clinical or regulated infrastructure status
- fully hardened production operations

The implemented flow should be treated as a production-style hosted baseline with explicit scope and maturity boundaries.
