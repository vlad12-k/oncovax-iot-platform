# ADR 0002: Use InfluxDB for time-series telemetry
## Status
Accepted
## Context
Telemetry is time-series and requires efficient writes, retention policies, and dashboard querying.
## Decision
Use InfluxDB for time-series telemetry in dev/prototype.
## Consequences
Pros: time-series native, retention support, Grafana integration.
Cons: self-hosted ops overhead; production may use managed TSDB.
Mitigations: docker-compose orchestration, retention configuration, export strategy.
