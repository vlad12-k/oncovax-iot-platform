# OncoVax Architecture Diagram

This diagram shows the canonical hosted baseline for the OncoVax IoT Platform: software simulators publish telemetry to Mosquitto over MQTT, the worker processes and persists time-series and operational/audit data to separate stores, and nginx ingress exposes a narrow public-safe health path while keeping operational API and Grafana surfaces protected. It represents a production-style deployment topology with explicit trust boundaries, while remaining non-clinical and non-certified.

```mermaid
flowchart LR
    classDef infra fill:#f5f7fa,stroke:#6b7280,stroke-width:1px,color:#111827;
    classDef public fill:#ecfdf5,stroke:#059669,stroke-width:1px,color:#065f46;
    classDef protected fill:#fff7ed,stroke:#c2410c,stroke-width:1px,color:#7c2d12;
    classDef store fill:#eef2ff,stroke:#4338ca,stroke-width:1px,color:#1e1b4b;
    classDef note fill:#f9fafb,stroke:#9ca3af,stroke-dasharray: 4 3,color:#374151;

    ext[External user / operator client]:::infra

    subgraph host[Hosted baseline: cloud VM / server]
        sim[Software telemetry simulator(s)]:::infra
        mqtt[Mosquitto MQTT broker]:::infra
        worker[Worker service]:::infra
        api[FastAPI service]\n(api + dashboard):::infra
        nginx[nginx ingress]:::infra
        grafana[Grafana]:::protected

        subgraph persistence[Persistence responsibilities]
            influx[(InfluxDB\nTime-series telemetry + alerts)]:::store
            mongo[(Operational persistence boundary\nMongoDB / Atlas-backed via MONGO_URI)]:::store
        end

        sim -->|MQTT telemetry| mqtt
        mqtt --> worker
        worker -->|telemetry + alert signals| influx
        worker -->|alert lifecycle / audit records| mongo
        api -->|operational reads / updates| mongo
        grafana -->|query| influx

        nginx -->|/public-health| api
        nginx -->|protected operational paths| api
        nginx -->|protected Grafana path| grafana
    end

    ext -->|HTTPS| nginx

    pubSurf[Public-safe surface\n/public-health only]:::public
    protSurf[Protected operational surfaces\nAPI dashboard/alerts/summary + Grafana]:::protected
    simNote[Simulated telemetry source\n(no physical medical devices)]:::note
    statusNote[Non-clinical / non-certified deployment status]:::note

    nginx -. maps .-> pubSurf
    nginx -. enforces auth on .-> protSurf
    sim -.-> simNote
    host -.-> statusNote
```

## Legend

- **Public-safe surface**: intentionally limited ingress path for non-sensitive liveness exposure (for example `/public-health`).
- **Protected operational surface**: authenticated operator-facing API/dashboard and Grafana routes; not anonymous public dashboards.
- **Simulated telemetry source**: software simulators that generate telemetry events for ingestion and monitoring flows.
- **Hosted baseline boundary**: cloud VM/server deployment boundary containing ingress, processing, and persistence services.
