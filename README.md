# OncoVax IoT Platform

OncoVax is an event-driven cold-storage monitoring platform baseline that demonstrates software-telemetry ingestion, threshold-based alerting, operational APIs, and observability in a hosted deployment context.

The repository implements a production-style architecture (MQTT transport, worker processing, time-series storage, operational persistence, API/dashboard delivery, and ingress controls) while keeping scope boundaries explicit: telemetry is software-simulated, this is not certified clinical infrastructure, and additional hardening is required before full release-grade production treatment.

## What this project is

- A concrete implementation of an event-driven monitoring stack:
  - simulator -> MQTT -> worker -> InfluxDB + MongoDB -> FastAPI/dashboard -> Grafana.
- A hosted-baseline deployment model with documented ingress boundaries and operational checks.
- A technical reference for operational behavior with conservative, evidence-based claims.

## What this project is not

- Not a physical medical-device fleet platform.
- Not a certified clinical or regulated deployment.
- Not an anonymous public operational dashboard deployment.
- Not a claim of fully complete production hardening.

## Key capabilities

- Software-simulated telemetry ingestion through MQTT transport.
- Threshold-based worker alert generation over incoming telemetry.
- Split persistence model:
  - InfluxDB for telemetry and alert-series time-series data.
  - MongoDB for operational lifecycle/audit state.
- Operational API and dashboard workflows for health, summary, alert visibility, and acknowledgement.
- Production-like ingress model with public-safe versus protected operational route boundaries.
- Grafana-backed observability for time-series telemetry and alert-signal interpretation.
- Hosted baseline support across core services.
- Atlas-backed operational persistence compatibility via `MONGO_URI`.

## End-to-end workflow

1. Simulator publishes software telemetry events.
2. Mosquitto transports telemetry topics.
3. Worker validates payloads and evaluates thresholds.
4. InfluxDB stores telemetry and alert-series signals.
5. MongoDB stores operational lifecycle/audit state.
6. API/dashboard exposes operational views and acknowledgement interactions.
7. Grafana provides observability views over InfluxDB time-series data.
8. In production-like mode, nginx governs public-safe versus protected ingress surfaces.

## Architecture

The architecture is presented with **two diagrams** to separate runtime behavior from hosted deployment context.

### 1) Runtime / service architecture

![OncoVax Runtime Architecture](docs/assets/oncovax-architecture-diagram.svg)

This diagram explains how the system works internally: telemetry ingestion, worker processing, persistence responsibilities, API/dashboard access paths, and observability flow.

### 2) Hosted / infrastructure topology

![OncoVax Hosted Infrastructure Topology](docs/assets/oncovax-hosted-infrastructure-topology.svg)

This diagram explains hosted deployment context: live-domain ingress identity, DigitalOcean-style hosting substrate, VM/server boundary, external uptime-signal context, and Atlas-backed persistence compatibility boundary.

Companion interpretation and legend notes: [`docs/architecture-diagram.md`](docs/architecture-diagram.md)

## Hosted baseline and infrastructure roles

### Hosted baseline in practice

The hosted baseline runs on a Linux cloud VM/server boundary. That VM is the runtime boundary where ingress policy, service composition, restart behavior, and environment configuration are applied to the running stack.

DigitalOcean-style hosting is deployment substrate context for this baseline. It describes where the workload is hosted, not an application-layer feature and not a provider-guarantee claim.

The live domain is the ingress identity boundary for hosted operator and check access. In production-like topology (`infra/docker-compose.prod.yml` + `infra/nginx/nginx.conf`), nginx enforces route-level separation between public-safe and protected operational paths.

External uptime monitoring is an availability-signal layer for hosted public endpoint reachability.

It does **not** prove:

- internal worker processing correctness
- persistence integrity correctness
- protected operational workflow correctness

MongoDB Atlas compatibility is the managed persistence compatibility boundary for operational state through `MONGO_URI`. It represents supported persistence placement, not a claim of complete managed-service operational guarantees.

## System components and responsibilities

- **Simulator (`services/simulator/`)**: publishes software-generated telemetry.
- **Orchestration adapter (`services/orchestration_adapter/`)**: bridges demo/runtime-control MQTT topics.
- **Mosquitto**: MQTT broker for telemetry and control-topic transport.
- **Worker (`services/worker/`)**: validates payloads, applies threshold logic, writes telemetry and alert lifecycle records.
- **InfluxDB**: time-series telemetry and alert-series store.
- **MongoDB**: operational lifecycle/audit persistence boundary used by API workflows.
- **FastAPI + dashboard (`services/api/` + `services/web/`)**: health and operational APIs plus dashboard experience.
- **Grafana (`grafana/`)**: InfluxDB-backed observability views.
- **nginx ingress (`infra/nginx/nginx.conf`)**: route/auth boundary in production-like topology.

## Deployment modes

- **Local/dev** (`infra/docker-compose.dev.yml`)
  - Includes simulator, orchestration adapter, Mosquitto, worker, API/UI, InfluxDB, MongoDB, Grafana, and Node-RED.
  - Intended for local development and end-to-end runtime validation.

- **Hosted baseline** (`infra/docker-compose.yml`)
  - Core hosted stack: Mosquitto, worker, API, InfluxDB, MongoDB.
  - Supports Atlas-backed persistence via `MONGO_URI`.

- **Production-like ingress** (`infra/docker-compose.prod.yml` + nginx)
  - Adds nginx ingress boundary, TLS mounting, protected routes, simulator, orchestration adapter, and Grafana.
  - Aligns with hosted topology validation and ingress policy checks.

See: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

## Repository structure

- `infra/` — Docker Compose topologies, ingress config, and environment templates.
- `services/` — API, worker, simulator, and orchestration adapter service implementations.
- `grafana/` — dashboard definitions and provisioning artifacts.
- `docs/` — canonical architecture, deployment, observability, runbook, security, and evidence documentation.
- `scripts/` — operational helper scripts, including smoke-test entrypoints.
- `tests/` — repository verification and guardrail tests.
- `demo/` — demo-facing runtime artifacts and scenario support assets.

## Verification and proof surfaces

Implementation-backed checks and proof surfaces include:

- ingress public-safe liveness: `GET /public-health`
- API liveness: `GET /health`
- operational summary surface: `GET /summary`
- operational alert visibility surface: `GET /alerts`
- Grafana dashboards over InfluxDB time-series data
- container/service logs across API, worker, simulator, ingress, and data services
- runbook-driven restart, recovery, and rollback checks
- claim-to-proof mapping in [`docs/EVIDENCE_MAP.md`](docs/EVIDENCE_MAP.md)

Canonical validation entrypoints:

```bash
make verify-local
./scripts/smoke_test.sh --prod <domain> <username> <password>
```

## Live hosted observability evidence (deployed baseline)

The following screenshots are from the live hosted Grafana baseline and provide visible supporting evidence for deployed observability behavior:

![Live hosted Grafana — Temperature by device](docs/assets/live-hosted/live-hosted-grafana-temperature-by-device.png)
_Caption: Device-level temperature trends visible from the deployed hosted baseline._

![Live hosted Grafana — Recent active alerts (last 50)](docs/assets/live-hosted/live-hosted-grafana-recent-active-alerts-last-50.png)
_Caption: Recent alert activity surface from the deployed hosted baseline._

These visuals are supporting proof layers and should be interpreted together with API checks, logs, runbook verification, and configuration-backed runtime behavior.

## Live walkthrough video

A live hosted walkthrough of the deployed baseline is available here:  
https://youtu.be/Q5hKVtd-a3g

This video is a supporting demonstration layer and should be interpreted alongside API checks, logs, runbook validation, and documented scope boundaries.

## Security and operational boundaries

Current baseline controls include:

- ingress segmentation between public-safe and protected surfaces
- basic-auth protections for operational and Grafana ingress surfaces in production-like mode
- nginx rate limits on protected routes (including acknowledgement write paths)
- runbook and recovery/rollback procedures
- observability baseline through API checks, logs, InfluxDB, and Grafana where available

These are baseline controls, not complete production hardening.

## Current maturity

This repository represents a serious production-style hosted baseline with implemented runtime services, ingress boundaries, operational documentation, and verification paths.

It is not yet fully release-grade production infrastructure. Additional hardening, deeper application-layer security controls, and environment-specific operational assurance are still required before full production treatment.

## Documentation map

- Overview: [`docs/OVERVIEW.md`](docs/OVERVIEW.md)
- Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Architecture diagrams: [`docs/architecture-diagram.md`](docs/architecture-diagram.md)
- Data flow: [`docs/DATA_FLOW.md`](docs/DATA_FLOW.md)
- Deployment: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
- Observability: [`docs/OBSERVABILITY.md`](docs/OBSERVABILITY.md)
- Operations runbook: [`docs/RUNBOOK.md`](docs/RUNBOOK.md)
- Operator quick reference: [`OPS_RUNBOOK.md`](OPS_RUNBOOK.md)
- Recovery/rollback: [`docs/RECOVERY_AND_ROLLBACK.md`](docs/RECOVERY_AND_ROLLBACK.md)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Threat model: [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md)
- Known limitations: [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md)
- Evidence map: [`docs/EVIDENCE_MAP.md`](docs/EVIDENCE_MAP.md)
- Final validation checklist: [`docs/FINAL_VALIDATION_CHECKLIST.md`](docs/FINAL_VALIDATION_CHECKLIST.md)
- Production hardening roadmap: [`docs/PRODUCTION_HARDENING_DAY1_DAY5.md`](docs/PRODUCTION_HARDENING_DAY1_DAY5.md)

## Non-claims

This repository does **not** claim:

- telemetry from physical medical-device fleets
- certified clinical or regulated deployment status
- complete production hardening or complete security assurance

Use this repository as a production-style engineering baseline with explicit operational boundaries and conservative claim discipline.

## License and usage

This repository is **source-available** and is **not** offered under a permissive open-source license.

See [`LICENSE`](LICENSE) for legal terms and [`LICENSE_POLICY.md`](LICENSE_POLICY.md) for a plain-language summary.
