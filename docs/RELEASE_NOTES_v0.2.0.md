# v0.2.0 — Product Baseline & Deployment Lifecycle Release

## Product baseline

OncoVax provides software-simulated MQTT ingestion, temperature excursion detection, InfluxDB time-series storage, MongoDB alert lifecycle records, FastAPI operator workflows, and Grafana observability.

This release makes the repository's product scope and deployment lifecycle explicit. The previously validated DigitalOcean deployment was intentionally decommissioned for cost control after cloud credits were exhausted. Configuration and historical evidence remain available for inspection and future provisioning.

## Changes

- Product-focused entrypoint, deployment guidance, evidence catalog and release gates.
- Durable test/screenshot names and updated references; historical screenshot contents and checksum archive preserved.
- Worker-generated alert and persisted audit contracts with positive and negative tests; unused metadata/profile scaffolding removed.
- CI runs pytest, syntax/configuration checks and a local Docker pipeline round trip.
- `make verify-static` and `make verify-local` share one validation route; HTTP failures now fail smoke checks.
- Local service ports bind to loopback, and local Grafana receives provisioned datasource/dashboard configuration.

## Compatibility and limitations

Existing API routes, MQTT topics, dashboard UID, license terms and contributor attribution are retained. Documentation and screenshot paths changed. Local clients on other machines can no longer reach development ports without an explicit operator configuration change.

The alert schema now describes worker output using `ts`; the audit schema describes persisted/API records using `time`. These contracts are tested against implementation; only telemetry has runtime schema enforcement. Consumers of the previous documentation-only schemas should review the new definitions.

This release does not establish clinical certification, regulatory compliance, complete application RBAC, immutable audit logging or guaranteed recovery. Historical deployment observations do not prove current availability. Publishing this release requires review of the CI results and the [release checklist](FINAL_VALIDATION_CHECKLIST.md).
