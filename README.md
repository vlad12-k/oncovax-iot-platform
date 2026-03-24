# OncoVax IoT Monitoring Platform

Event-driven IoT monitoring platform for regulated cold-storage environments. This repository is maintained as a **production-like operations baseline** and is evolved incrementally with deployment safety guardrails.

## Recruiter / instructor quick review (10–15 minutes)

If you are evaluating this project for clarity, delivery quality, and demonstrable outcomes, use this path:

1. Read [docs/OVERVIEW.md](docs/OVERVIEW.md) for scope and capability baseline.
2. Follow [docs/DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md) for a single end-to-end demo sequence.
3. Use [docs/EVIDENCE_MAP.md](docs/EVIDENCE_MAP.md) to map claims to concrete proof artifacts.
4. Browse [demo/screenshots/README.md](demo/screenshots/README.md) for visual evidence grouped by proof surface.
5. (Optional live check) run production-like smoke validation from [docs/RUNBOOK.md](docs/RUNBOOK.md).

## What this repository demonstrates

- MQTT-based telemetry ingestion pipeline
- Worker-side validation and alert event generation
- Time-series storage in InfluxDB
- Audit/event persistence in MongoDB / MongoDB Atlas
- FastAPI operational endpoints and lightweight dashboard
- Docker Compose dev and production-like deployment layouts
- Nginx ingress with protected routes and public uptime probe

## Deployment safety commitments

This repository intentionally preserves the existing production-safe behavior:

- `/public-health` remains available for unauthenticated uptime checks
- Private routes remain protected through ingress auth controls
- Production reverse-proxy and compose topology are additive-first
- Secrets are never committed to source control

## Current architecture flow

```text
Simulator -> MQTT -> Worker -> InfluxDB (telemetry + alerts)
                           -> MongoDB/Atlas (audit + alert lifecycle)
                                        ^
                                      FastAPI
                                        ^
                                   Web dashboard
```

## Quickstart (local dev stack)

```bash
docker compose -f infra/docker-compose.dev.yml up -d --build
./scripts/smoke_test.sh
```

Then continue with:

- End-to-end demo flow: [docs/DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md)
- Scenario-oriented narration: [docs/DEMO_SCENARIOS.md](docs/DEMO_SCENARIOS.md)
- Observability dashboard import/use: [grafana/README.md](grafana/README.md)

## Repository structure

```text
infra/                  Compose and ingress configuration
services/
  api/                  FastAPI service
  worker/               Telemetry consumer and alert logic
  simulator/            Telemetry publisher
  web/                  Dashboard frontend assets
schemas/                Message and record schema files
docs/                   Architecture, runbooks, hardening and operations guides
flows/                  Node-RED export placeholders/artifacts
grafana/                Dashboard export placeholders/artifacts
```

## Operations and delivery docs

- [docs/OVERVIEW.md](docs/OVERVIEW.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DATA_FLOW.md](docs/DATA_FLOW.md)
- [docs/DEMO_WALKTHROUGH.md](docs/DEMO_WALKTHROUGH.md)
- [docs/RUNBOOK.md](docs/RUNBOOK.md)
- [docs/PRODUCTION_HARDENING_DAY1_DAY5.md](docs/PRODUCTION_HARDENING_DAY1_DAY5.md)
- [docs/DEMO_SCENARIOS.md](docs/DEMO_SCENARIOS.md)
- [docs/EVIDENCE_MAP.md](docs/EVIDENCE_MAP.md)
- [docs/RECOVERY_AND_ROLLBACK.md](docs/RECOVERY_AND_ROLLBACK.md)
- [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md)
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)

## Artifact placeholders introduced in Phase A

- `flows/` for future Node-RED exports
- `grafana/dashboards/` for future Grafana dashboard exports
- `services/simulator/scenarios/` for simulator scenario templates
- Additional schema placeholders for alert/audit/device metadata contracts

## Important notes

- Do not commit `.env` files or live credentials.
- Preserve ingress and auth behavior when making runtime changes.
- Prefer additive updates and explicit documentation over destructive rewrites.
