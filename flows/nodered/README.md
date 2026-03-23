# Node-RED Demo Control Flow (Phase B2c)

This directory contains an **optional, dev/demo-only** Node-RED flow artifact for demo orchestration controls.

## Artifact

- `demo-control-flow.json`

Import into Node-RED via **Menu → Import → Clipboard/File**.

## Approved demo-control MQTT contract

### Control topics (subscribed by flow)

- `oncovax/demo/control/scenario/select`
- `oncovax/demo/control/mode/set`
- `oncovax/demo/control/event/trigger`

### Status topic (published by flow)

- `oncovax/demo/orchestration/status`

## Command payload shape (basic)

All command payloads are expected to be JSON object payloads (or JSON strings parseable into objects) with:

- `command_id` (string, required)
- `issued_at` (string timestamp, required)

Plus command-specific required fields:

- `scenario/select`: `scenario` (string)
- `mode/set`: `mode` (string), optional `enabled` (boolean), optional `profile` (string)
- `event/trigger`: `event` (string), optional `data` (object)

## Status payload behavior

The flow emits a status object to `oncovax/demo/orchestration/status` for each command:

- `status`: `accepted` or `rejected`
- `source_topic`
- `command_type`
- `command_id` when available
- `reason` when rejected
- `received_at`
- `contract_version` (`1.0`)

## Safety boundary

This flow **does not** change canonical ingestion routing and is not required for ingestion correctness.

- Authoritative ingestion path remains: `MQTT -> worker`.
- Canonical telemetry topics remain separate from demo-control topics.
- This flow is intentionally constrained to `oncovax/demo/**` topics.
