# ADR 0003: Separate worker for stream processing and alert logic
## Status
Accepted
## Context
Excursion detection (duration-based), deduplication, and alert routing are stream processing tasks.
## Decision
Implement a dedicated `worker` subscribed to MQTT to validate schemas, write to TSDB, and emit alerts/audit events.
## Consequences
Pros: scalable, resilient, clean separation from API.
Cons: more moving parts.
Mitigations: health checks, runbook, integration tests.
