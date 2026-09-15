# Runtime Verification Walkthrough

## Local preparation

Install the development requirements and run `make verify-local` as described in the [README](../README.md). This checks the source/configuration, starts the local stack, and exercises telemetry ingestion through acknowledgement. Local data and the uniquely named verification probe remain available for inspection.

## Operator workflow

1. Open `http://localhost:8000/` and inspect health, alert totals and the alert register.
2. Retrieve `/alerts?acknowledged=false`, open an alert by ID, and acknowledge it with an operator name and incident note.
3. Check `/summary` and the refreshed record. Acknowledgement updates MongoDB lifecycle state; it does not append an immutable audit event.
4. Open Grafana at `http://localhost:3000/` and inspect the provisioned OncoVax Observability dashboard. Check temperature, ingest rate, recent alerts and device metrics.
5. Use the optional [Node-RED flow](../flows/nodered/README.md) to send `scenario/select`, `mode/set` and temporary runtime events. Watch adapter status and metric changes. Reset runtime when finished.

The [scenario guide](DEMO_SCENARIOS.md) and [Grafana guide](../grafana/README.md) explain controls and expected signals.

## Historical hosted validation

The DigitalOcean deployment was previously validated and intentionally decommissioned after cloud credits were exhausted. The [archive](DEPLOYMENT_ARCHIVE.md), [screenshots](../demo/screenshots/README.md) and [recording](https://youtu.be/Q5hKVtd-a3g) document earlier observations.

These artifacts do not indicate current service availability. To validate hosting again, provision a host and hostname you control, follow the [deployment guide](DEPLOYMENT.md), then run `./scripts/smoke_test.sh --prod <domain> <username> <password>`. Verify unauthenticated requests are rejected on protected routes and inspect Grafana separately.
