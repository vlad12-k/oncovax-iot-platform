# Simulator Service (Phase B)

This directory contains an additive simulator runtime at `main.py` that continuously publishes realistic, multi-device telemetry to MQTT.

`services/simulator/simulator.py` remains untouched for backward compatibility.

## Files

- `main.py` — JSON-driven multi-device simulator
- `devices.json` — expanded fleet catalog and baseline telemetry profiles
- `scenarios.json` — scenario mode definitions and demo profile defaults
- `requirements.txt` — Python dependencies

## Fleet model

The simulator now ships with a richer fleet (16 devices total) covering all target asset types:

- 4 × vaccine fridge
- 4 × transport box
- 4 × clinic freezer
- 4 × warehouse cold room

Each device includes metadata suitable for demo dashboards:

- `device_id`
- `asset_type`
- `site`
- `zone`
- `fleet_group`
- `firmware_version`
- `status`
- `location` (`lat`/`lon`)

## Telemetry payload format

Each published message is JSON with this structure:

```json
{
  "timestamp": "2026-03-23T13:00:00.123456+00:00",
  "device_id": "vf-001",
  "asset_type": "vaccine fridge",
  "site": "NYC Clinic A",
  "zone": "immunization-room-1",
  "fleet_group": "metro-east-clinics",
  "firmware_version": "1.8.4",
  "temperature": 4.12,
  "humidity": 51.3,
  "battery": 97.86,
  "door_open": false,
  "open_duration_seconds": 0,
  "signal_strength": -61.4,
  "status": "normal",
  "ambient_temperature": 21.7,
  "setpoint_temperature": 4.0,
  "power_state": "on",
  "network_status": "online",
  "compressor_state": "cycling",
  "location": {
    "lat": 40.748816,
    "lon": -73.985429
  }
}
```

Notes:

- `compressor_state` is emitted for fixed cooling assets (fridge/freezer/cold room) and omitted for transport boxes.
- `open_duration_seconds` tracks continuous door-open duration.

## Supported scenario modes

- `normal` — baseline behavior
- `cold-chain breach` — intermittent temperature excursions
- `unstable battery` — accelerated battery drain + noisier signal
- `offline/recovery` — periodic offline windows and recovery windows
- `multi-device burst` — multiple publications per device each cycle
- `transport instability` — transport-box-specific thermal/signal volatility
- `prolonged door-open incident` — sustained door-open events and thermal rise
- `repeated breach pattern` — deterministic breach/normal cadence for escalation demos
- `demo-friendly` — guaranteed visible events in short windows

Scenarios are configured in `scenarios.json`, and devices/profiles are configured in `devices.json`.

## Demo-friendly profile

Use the `demo` profile to force visible events quickly, even on otherwise calm scenarios.

- CLI option: `--profile demo`
- Default scenario for demo profile: `demo-friendly`
- Behavior includes frequent door activity, periodic thermal spikes, and increased burst density.

## Running safely

From repository root:

```bash
python3 -m pip install -r /home/runner/work/oncovax-iot-platform/oncovax-iot-platform/services/simulator/requirements.txt
python3 /home/runner/work/oncovax-iot-platform/oncovax-iot-platform/services/simulator/main.py --dry-run --seed 42
```

Dry-run mode logs payloads without publishing anything.

To publish to local/dev MQTT only:

```bash
python3 /home/runner/work/oncovax-iot-platform/oncovax-iot-platform/services/simulator/main.py \
  --mqtt-host localhost \
  --mqtt-port 1883 \
  --mqtt-topic oncovax/telemetry/simulator \
  --scenario normal \
  --profile standard \
  --seed 42
```

Demo mode example:

```bash
python3 /home/runner/work/oncovax-iot-platform/oncovax-iot-platform/services/simulator/main.py \
  --dry-run \
  --profile demo \
  --interval-seconds 0.5 \
  --seed 42
```

To stop gracefully, press `Ctrl+C` (SIGINT) or send SIGTERM.

## Notes for pipeline visibility

This simulator publishes to `oncovax/telemetry/simulator` by default to avoid accidental interference.
If you want existing worker ingestion, point topic to the worker-consumed topic explicitly:

```bash
--mqtt-topic oncovax/telemetry
```

That routing choice is operational and should be made intentionally per environment.
