# Node-RED Demo Control Flow (Phase B2c)

This directory contains **optional, dev/demo-only** Node-RED flow exports.

## Demo-control contract flow

- File: `demo-control-flow.json`
- Scope: orchestration control/status for demos only
- Runtime role: receives approved demo control messages, validates basic command shape, and publishes orchestration status events

### Approved control topics (subscribe)

- `oncovax/demo/control/scenario/select`
- `oncovax/demo/control/mode/set`
- `oncovax/demo/control/event/trigger`

### Approved status topic (publish)

- `oncovax/demo/orchestration/status`

## Contract expectations

All control messages are JSON objects and include:

- `contract_version` (string)
- `command_id` (string)
- `issued_at` (string timestamp)
- `issued_by` (string)

Topic-specific required fields:

- `oncovax/demo/control/scenario/select`: `scenario` (string)
- `oncovax/demo/control/mode/set`: `enabled` (boolean)
- `oncovax/demo/control/event/trigger`: `event` (string)

The flow emits `accepted` or `rejected` status payloads on `oncovax/demo/orchestration/status`.

## Safety boundary

- This flow does **not** rewire ingestion and does **not** replace worker processing.
- Authoritative ingestion remains direct MQTT telemetry to worker (`oncovax/telemetry` and explicitly configured worker-compatible topics).
- Production correctness must not depend on Node-RED.
