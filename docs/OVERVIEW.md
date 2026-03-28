# Platform Overview

## 1) Platform summary

OncoVax is an event-driven cold-storage monitoring baseline that models telemetry ingestion, alert generation, operational APIs, and observability in a hosted deployment context.

The repository implements a production-style architecture (MQTT transport, worker-side processing, time-series storage, operational persistence, API/UI surfaces, and ingress controls) while remaining explicit about scope and maturity boundaries.

## 2) Core components

The current repository includes the following core components and responsibilities:

- **Simulator (`services/simulator/`)**
  - Publishes software-generated telemetry messages.

- **MQTT broker / transport (Mosquitto)**
  - Provides message distribution for telemetry topics.

- **Worker (`services/worker/`)**
  - Subscribes to telemetry topics, validates payloads, evaluates threshold conditions, writes telemetry/alert signals to InfluxDB, and persists alert workflow records to MongoDB.

- **InfluxDB**
  - Stores time-series telemetry and alert measurements.

- **MongoDB (local) / Atlas-backed persistence (`MONGO_URI`)**
  - Stores operational alert lifecycle and audit records.

- **FastAPI service (`services/api/`)**
  - Exposes health and operational endpoints (summary, alerts, acknowledgement workflows) and serves dashboard content.

- **Dashboard/UI (`services/web/`)**
  - Provides an operator-facing web interface for current system and alert state.

- **Grafana (`grafana/` + compose wiring)**
  - Provides observability dashboards backed by InfluxDB.

- **nginx ingress (`infra/nginx/nginx.conf`, production-like compose path)**
  - Provides HTTPS routing, basic-auth protection of operational surfaces, and route-level exposure boundaries.

## 3) Deployment modes

The project defines three primary deployment modes with different behavior and exposure properties:

- **Local/dev (`infra/docker-compose.dev.yml`)**
  - Full local stack for development and testing, including dev/demo tooling.

- **Hosted baseline (`infra/docker-compose.yml`)**
  - Core hosted reference stack for MQTT, worker, API, InfluxDB, and MongoDB.

- **Production-like ingress path (`infra/docker-compose.prod.yml` + nginx)**
  - Adds reverse-proxy ingress, TLS certificate mounting, protected routes, and production-style service restart behavior.

Environment behavior differs materially across these modes. Security assumptions, exposure controls, and operational procedures must be validated for the specific target environment.

## 4) Operational boundaries

Current operational boundaries are explicit:

- Telemetry in this repository is simulated.
- The repository does not include a physical device fleet.
- Operational API and dashboard surfaces are intended to be protected, not anonymous public endpoints.
- nginx exposes a public-safe health route (`/public-health`) for constrained liveness checks.
- The project is non-clinical in scope and is not represented as certified clinical or regulated infrastructure.

## 5) Current maturity

The project demonstrates a serious production-style architecture with a working hosted baseline, documented deployment/runbook/security guidance, and practical baseline controls.

At the same time, it should not be treated as fully release-grade production infrastructure without further hardening, stronger application-layer security controls, and environment-specific operational assurance.
