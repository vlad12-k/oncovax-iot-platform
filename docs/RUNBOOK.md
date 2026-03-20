# Runbook – OncoVax IoT Monitoring Platform

## Purpose

This runbook covers operational procedures for the OncoVax IoT Monitoring Platform, including service management, alert workflow, troubleshooting, and recovery steps.

---

## 1. Service Management

### Start local development stack

```bash
docker compose -f infra/docker-compose.dev.yml up -d --build
```

### Stop local development stack

```bash
docker compose -f infra/docker-compose.dev.yml down
```

### View logs (all services)

```bash
docker compose -f infra/docker-compose.dev.yml logs -f --tail=200
```

### View logs for a specific service

```bash
docker compose -f infra/docker-compose.dev.yml logs -f api
docker compose -f infra/docker-compose.dev.yml logs -f worker
```

### Restart a specific service

```bash
docker compose -f infra/docker-compose.dev.yml restart api
```

### Check service status

```bash
docker compose -f infra/docker-compose.dev.yml ps
```

---

## 2. Smoke Test

Run the included smoke test to verify all services are reachable:

```bash
./scripts/smoke_test.sh
```

Expected: all checks pass with `200 OK` or healthy responses.

---

## 3. API Checks

### Check API health

```bash
curl -s http://localhost:8000/health
# Expected: {"status":"ok"}
```

### Check alert summary

```bash
curl -s http://localhost:8000/summary | python -m json.tool
```

### List alerts (last 20)

```bash
curl -s "http://localhost:8000/alerts?limit=20" | python -m json.tool
```

### List unacknowledged alerts

```bash
curl -s "http://localhost:8000/alerts?acknowledged=false" | python -m json.tool
```

### Get a specific alert

```bash
curl -s http://localhost:8000/alerts/<alert_id> | python -m json.tool
```

### Acknowledge an alert

```bash
curl -s -X POST http://localhost:8000/alerts/<alert_id>/acknowledge \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by": "operator-name", "incident_note": "Reviewed and closed."}' \
  | python -m json.tool
```

---

## 4. Alert Workflow

1. Worker detects a temperature breach above `TEMP_THRESHOLD`
2. Alert record is written to MongoDB `audit_events` collection
3. Alert appears in the operational dashboard at `http://localhost:8000`
4. Operator reviews the alert in the dashboard (filter by unacknowledged)
5. Operator clicks **Acknowledge** on an alert row
6. Modal prompts for `acknowledged_by` and optional `incident_note`
7. API issues `POST /alerts/{id}/acknowledge`
8. Alert status updates to Acknowledged in the dashboard

---

## 5. Generating Test Telemetry

### Start the simulator

```bash
docker compose -f infra/docker-compose.dev.yml up simulator
```

The simulator publishes to `oncovax/telemetry` approximately once per second.
Excursion spikes (value ~10.5 °C) are injected randomly with ~2% probability.

### Manually trigger an excursion (for testing)

Use the Postman collection at `tools/postman_collection.json`, or publish directly:

```bash
docker exec mosquitto mosquitto_pub \
  -t oncovax/telemetry \
  -m '{"device_id":"test-001","asset_type":"coldstorage","ts":"2024-01-01T00:00:00+00:00","metric":"temperature","value":10.5,"unit":"C"}'
```

---

## 6. Troubleshooting

### API returns 503 / cannot connect to MongoDB

- Check that MongoDB container is running: `docker compose ps`
- Verify `MONGO_URI` env var is set correctly in `.env`
- For Atlas: verify the Atlas connection string is valid and network access is allowed

### Dashboard shows "No alerts"

- Confirm the worker is running and subscribed to MQTT
- Confirm the simulator is publishing messages
- Check `docker compose logs worker` for validation or connection errors
- Check that `TEMP_THRESHOLD` is set appropriately (default: 8.0 °C)

### Worker not writing to InfluxDB

- Verify `INFLUX_URL`, `INFLUX_TOKEN`, `INFLUX_ORG`, `INFLUX_BUCKET` are correct in `.env`
- Check InfluxDB health: `curl http://localhost:8086/health`

### Grafana shows "No data"

- Ensure the InfluxDB data source is configured in Grafana (URL: `http://influxdb:8086`)
- Confirm the token and org match the values set in `.env`
- Select an appropriate time window covering when the simulator was running

### Container restart loop

- Check container logs: `docker compose logs <service>`
- Confirm environment variables are correctly set in `.env`
- Confirm MongoDB or InfluxDB containers are healthy before API or worker

---

## 7. Rollback Procedure

### Local development

```bash
git log --oneline -10             # identify last known good commit
git checkout <commit-sha>         # revert working tree
docker compose -f infra/docker-compose.dev.yml down
docker compose -f infra/docker-compose.dev.yml up -d --build
```

### Hosted deployment (DigitalOcean)

1. SSH into the Droplet
2. Navigate to the deployment directory
3. Pull the previous image tag or revert to a prior `git` commit
4. Re-run `docker compose -f infra/docker-compose.prod.yml up -d --build`
5. Verify with `curl http://localhost:8000/health`

---

## 8. Data Management

### MongoDB – view audit records

```bash
docker exec -it mongodb mongosh oncovax \
  --eval 'db.audit_events.find({acknowledged: false}).limit(5).pretty()'
```

### InfluxDB – verify telemetry is arriving

Open `http://localhost:8086` in a browser, log in, and query the `telemetry` bucket.

---

## 9. Configuration Reference

All configuration is via environment variables. See `infra/.env.example` for the full list.

Key variables:

| Variable | Default | Description |
|---|---|---|
| `MONGO_URI` | `mongodb://mongodb:27017` | MongoDB connection string |
| `MONGO_DB` | `oncovax` | Database name |
| `MONGO_COLLECTION` | `audit_events` | Collection name |
| `INFLUX_URL` | `http://influxdb:8086` | InfluxDB base URL |
| `INFLUX_TOKEN` | dev token | InfluxDB API token |
| `INFLUX_ORG` | `oncovax` | InfluxDB organisation |
| `INFLUX_BUCKET` | `telemetry` | InfluxDB bucket |
| `MQTT_HOST` | `mosquitto` | MQTT broker hostname |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `TEMP_THRESHOLD` | `8.0` | Alert temperature threshold (°C) |
