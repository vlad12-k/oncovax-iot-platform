# Integration tests

This folder contains end-to-end checks for the MVP dataflow:

**simulator → MQTT → worker → InfluxDB → Grafana**

Planned tests (to be implemented):
1. Telemetry message is published to MQTT and consumed by the worker.
2. Schema validation rejects malformed telemetry.
3. Telemetry is persisted to InfluxDB with correct measurement/tags.
4. Excursion rule triggers an alert event when thresholds + duration are met.
5. Audit event is recorded for alert acknowledgement (later, MongoDB/Atlas).

How to run (placeholder):
- `make up`
- `make test-integration`
