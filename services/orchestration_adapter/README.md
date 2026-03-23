# Orchestration Adapter (D2)

Dev/demo-only adapter that subscribes approved control topics, validates commands,
and maps accepted commands to simulator internal runtime-control topic.

## Subscribed topics (unchanged)

- `oncovax/demo/control/scenario/select`
- `oncovax/demo/control/mode/set`
- `oncovax/demo/control/event/trigger`

## Published topics

- Status: `oncovax/demo/orchestration/status`
- Internal runtime control: `oncovax/demo/internal/simulator/runtime/control`

## Supported event_type values

- `burst_pulse`
- `breach_pulse`
- `offline_pulse`
- `reset_runtime`
