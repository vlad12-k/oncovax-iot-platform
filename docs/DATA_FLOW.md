# Data Flow

This document describes the current and planned data flow for OncoVax IoT operations.

## Ingestion pipeline

1. Simulator publishes telemetry messages to MQTT topic `oncovax/telemetry`.
2. Worker subscribes to telemetry topic and validates payload shape.
3. Worker writes telemetry time-series records to InfluxDB.
4. Worker evaluates alert conditions and writes alert/audit records to MongoDB/Atlas.
5. API reads Mongo records for dashboard and operator workflows.

## Storage responsibilities

- **InfluxDB**: time-series telemetry and alert signals suitable for charting.
- **MongoDB/Atlas**: alert lifecycle, acknowledgements, audit-style event records, and metadata.

## Monitoring and access

- Grafana consumes InfluxDB for visualization.
- API exposes health and alert summary/list/detail endpoints.
- Public monitoring uses `/public-health` route at ingress.

## Phase A note

This phase adds documentation and repository structure only. Runtime message handling and route behavior are intentionally unchanged.
