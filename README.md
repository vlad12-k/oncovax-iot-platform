# OncoVax IoT Platform

OncoVax is an event-driven cold-storage monitoring platform baseline that demonstrates telemetry ingestion, threshold-based alerting, operational APIs, and observability in a hosted deployment context.

The repository implements a production-style architecture (MQTT transport, worker processing, time-series storage, operational persistence, API/dashboard delivery, and ingress controls) while keeping scope boundaries explicit: telemetry is software-simulated, not physical medical-device telemetry; this is not certified clinical infrastructure; and additional hardening is required before full release-grade production treatment.

## What this project is

- A repository implementation of an event-driven monitoring pipeline:
  - simulator -> MQTT -> worker -> InfluxDB + MongoDB -> FastAPI/dashboard -> Grafana.
- A hosted-baseline deployment model with production-like ingress topology available in the repository.
- A concrete operational reference for ingress boundaries, runbook discipline, and evidence-backed claims.

## What this project is not

- Not a physical medical-device fleet platform.
- Not a certified clinical or regulated deployment.
- Not an anonymous public dashboard deployment.
- Not a claim of fully complete production hardening.

## Architecture at a glance

![OncoVax Architecture Diagram](docs/assets/oncovax-architecture-diagram.svg)

Architecture legend and interpretation: [`docs/architecture-diagram.md`](docs/architecture-diagram.md)

### Core runtime components

- **Simulator (`services/simulator/`)** publishes software-generated telemetry.
- **Mosquitto (MQTT)** provides message transport.
- **Worker (`services/worker/`)** validates payloads, evaluates thresholds, and writes to persistence layers.
- **InfluxDB** stores telemetry and alert-series time-series data.
- **MongoDB** stores operational alert lifecycle/audit records.
- **FastAPI (`services/api/`)** exposes health/summary/alerts/acknowledgement APIs and serves dashboard assets.
- **Grafana** provides InfluxDB-backed observability views.
- **nginx ingress (`infra/nginx/nginx.conf`)** enforces route exposure boundaries in production-like topology.

## Hosted baseline and infrastructure roles

### Where the stack runs

The hosted baseline is designed to run on a Linux cloud VM/server substrate (DigitalOcean-style hosting is documented as an example operating context). In this model, the VM is the runtime boundary for core services and ingress policy.

This is an implemented deployment context, not a claim of provider-managed production guarantees.

### Role of nginx and live domain ingress

In production-like topology (`infra/docker-compose.prod.yml` + `infra/nginx/nginx.conf`):

- nginx terminates ingress and routes traffic by host/path policy.
- `GET /public-health` is exposed as a narrow public-safe liveness route.
- Operational API/dashboard routes are protected by basic auth.
- Grafana host routing is protected by basic auth.
- TLS/domain behavior is operator-managed through deployment configuration.

The live domain is the ingress identity boundary for hosted checks and operator access, not proof of full production readiness.

### Role of MongoDB / Atlas-backed persistence

Operational persistence is defined by MongoDB-backed alert lifecycle/audit records. The same application contract supports Atlas-backed operation through `MONGO_URI`.

Atlas compatibility indicates managed persistence support for this boundary; it does not by itself claim broader managed-service guarantees beyond repository scope.

### Role of external uptime monitoring

External uptime checks are an availability-signal layer for hosted public endpoint reachability (for example, public-safe route liveness).

They do **not** prove complete internal correctness across worker processing, persistence integrity, or protected operational workflows.

## Deployment modes

- **Local/dev**: `infra/docker-compose.dev.yml` (full dev stack, direct local exposure)
- **Hosted baseline**: `infra/docker-compose.yml` (core hosted services)
- **Production-like ingress**: `infra/docker-compose.prod.yml` + nginx (ingress boundary, protected operational surfaces)

See: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

## Security and operational boundaries

Currently represented baseline controls include:

- ingress separation between public-safe and protected operational surfaces
- TLS scaffolding and route protection in nginx production-like policy
- selected rate-limiting in nginx for protected/write-sensitive paths
- runbook and recovery/rollback procedures
- observability baseline through API checks, logs, InfluxDB, and Grafana (where present)

These are baseline controls, not full production-hardening completion.

## Local verification

Canonical local verification path:

```bash
make verify-local
```

Production-like smoke path (hosted environment required):

```bash
./scripts/smoke_test.sh --prod <domain> <username> <password>
```

## Documentation map

- Overview: [`docs/OVERVIEW.md`](docs/OVERVIEW.md)
- Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
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

- physical medical-device telemetry fleet operation
- certified clinical or regulated deployment status
- complete production hardening or complete security assurance

Use this repository as a production-style engineering baseline with explicit operational boundaries and evidence-based claim discipline.
