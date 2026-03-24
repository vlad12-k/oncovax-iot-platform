# Grafana Artifacts

This directory contains **repo-controlled Grafana artifacts** for Prompt F final observability.

## Files

- `dashboards/oncovax-observability-final.v1.json` — finalized dashboard export for live telemetry + alerts + D2 runtime-control visibility.

## Dashboard scope (Prompt F final)

The dashboard is designed to provide live evidence that the current system is working end-to-end:

- telemetry flow is active
- excursion alerts are generated and visible
- per-device behavior is visible
- D2 runtime-control actions create visible changes
- ingestion remains aligned with existing B2a/B2b/D2/E data path

## Data source requirements

Use an InfluxDB (Flux) data source configured against the same bucket used by worker writes:

- URL: `http://influxdb:8086`
- Org: `oncovax`
- Bucket: `telemetry`
- Token: use your local/dev token from `.env` (`INFLUX_TOKEN`)

The export uses a datasource input placeholder named `DS_INFLUXDB`; map it to your Influx data source during import.

## Import in Codespaces / dev

1. Start dev stack:

   ```bash
   docker compose -f infra/docker-compose.dev.yml up -d --build
   ```

2. Open Grafana: `http://localhost:3000`
3. Configure InfluxDB datasource (if not already present).
4. Import dashboard:
   - Grafana → **Dashboards** → **Import**
   - Upload `grafana/dashboards/oncovax-observability-final.v1.json`
   - Select your InfluxDB datasource for `DS_INFLUXDB`
5. Set dashboard time range to **Last 30 minutes** (or broader if needed).

## Final panels

1. **Telemetry ingest (points/min)** (stat)
2. **Active alerts (events/min)** (stat)
3. **Devices seen in window** (stat)
4. **Door-open state distribution** (pie)
5. **Temperature by device** (timeseries)
6. **Humidity and battery trends** (timeseries)
7. **Signal strength (offline pulse visibility)** (timeseries)
8. **Alert intensity (value - threshold)** (timeseries)
9. **Recent active alerts (last 50)** (table)
10. **Latest metrics by device** (table)

## Live verification behavior

With simulator + worker running, these should move continuously:

- **Telemetry ingest (points/min)** increases above 0 and updates each minute.
- **Temperature/Humidity/Battery/Signal** timeseries continue updating.
- **Latest metrics by device** refreshes with recent values.

When alerts are generated (temperature breaches):

- **Active alerts (events/min)** rises above 0.
- **Recent active alerts** shows new rows with device/metric/value/threshold/message.
- **Alert intensity** shows positive deltas (`value - threshold`) for active breaches.

### D2 runtime-control visibility expectations

After issuing commands (via existing control topics):

- `scenario/select`:
  - persistent behavior shift across trend panels (temperature, humidity/battery, door state distribution), based on selected scenario dynamics.
- `mode/set`:
  - persistent profile change; demo/standard mode shifts event cadence and trend characteristics visible in ingest + trend panels.
- `burst_pulse`:
  - short-term increase in **Telemetry ingest (points/min)** and denser points in trend panels.
- `breach_pulse`:
  - temperature spikes in **Temperature by device**, followed by alert activity and higher **Alert intensity**.
- `offline_pulse`:
  - **Signal strength** drops toward `-120 dBm`, with corresponding behavior change visible in trends.
- `reset_runtime`:
  - trend behavior returns toward startup scenario/profile baseline; temporary pulse effects clear.

## Notes

- No secrets are embedded in the dashboard JSON.
- Dashboard panels show **No data** when no telemetry exists in selected window.
- This layer is additive and does not change worker/simulator/orchestration ingestion logic.
