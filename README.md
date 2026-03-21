# OncoVax IoT Monitoring Platform

Event-driven IoT monitoring platform for regulated cold-storage environments. This repository represents a **production-like, release-candidate baseline** rather than a fully hardened production system.

## Release-candidate overview

The platform demonstrates a complete telemetry-to-alert workflow:

```
Simulator → MQTT → Worker → InfluxDB (telemetry + alerts)
                         → MongoDB / Atlas (audit records)
                               ↑
                          FastAPI API
                               ↑
                      Operational Dashboard
```

## Current capabilities

- Telemetry schema validation (`schemas/telemetry.schema.json`)
- Python simulator publishing MQTT telemetry
- Python worker validating telemetry, detecting excursions, and writing:
  - InfluxDB time-series data
  - MongoDB audit-trail records
- FastAPI REST API:
  - `GET /health`, `GET /summary`, `GET /alerts`, `GET /alerts/{id}`
  - `POST /alerts/{id}/acknowledge`
- Lightweight HTML/CSS/JS dashboard served by the API
- MongoDB Atlas integration baseline (via `MONGO_URI`)
- DigitalOcean hosted baseline (API + dashboard)
- Docker Compose dev/base/prod-like stacks
- CI / code-quality baseline (GitHub Actions, CodeQL, Dependabot)
- Smoke test script for basic readiness checks

## Environments

- **Local full-stack development** (`infra/docker-compose.dev.yml`)
  - Runs Mosquitto, InfluxDB, MongoDB, FastAPI, Grafana, and Node-RED
  - Suitable for end-to-end demos with simulated telemetry

- **Hosted baseline (DigitalOcean + MongoDB Atlas)**
  - FastAPI + dashboard hosted on a Droplet
  - Audit data stored in Atlas (`MONGO_URI`)
  - Local MongoDB container is not required in this mode

- **Production-like deployment (nginx + TLS)**
  - `infra/docker-compose.prod.yml` adds nginx reverse proxy and TLS scaffold
  - Requires real certificates and further hardening before live production

## Local development quickstart

```bash
docker compose -f infra/docker-compose.dev.yml up -d --build
./scripts/smoke_test.sh
```

## Repository structure

```
infra/                  Docker Compose configs, nginx, env examples
services/
  simulator/            Telemetry publisher
  worker/               Telemetry consumer + excursion detection
  api/                  FastAPI service
  web/                  Dashboard frontend
  tools/                Utility scripts
schemas/                Telemetry JSON schema
scripts/                Smoke tests and utilities
docs/                   Architecture, runbook, threat model, deployment docs
demo/                   Scenario screenshots and write-ups
```

## Current limitations

- No authentication or role-based access control
- TLS termination is scaffolded but not fully hardened
- Lightweight UI only (no full operational web app)
- Hosted baseline does not represent a complete production deployment

## Documentation

- [docs/OVERVIEW.md](docs/OVERVIEW.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)
