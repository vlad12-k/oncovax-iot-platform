# Simulator Service (Phase B)

This directory now contains an additive simulator runtime at `main.py` that continuously publishes realistic multi-device telemetry to MQTT.

`services/simulator/simulator.py` remains untouched for backward compatibility.

## Files

- `main.py` — JSON-driven multi-device simulator
- `devices.json` — device catalog and baseline telemetry profiles
- `scenarios.json` — scenario mode definitions
- `requirements.txt` — Python dependencies (already present)

## Telemetry payload format

Each published message is JSON with this structure:

```json
{
  "timestamp": "2026-03-23T13:00:00.123456+00:00",
  "device_id": "vf-001",
  "asset_type": "vaccine fridge",
  "temperature": 4.12,
  "humidity": 51.3,
  "battery": 97.86,
  "door_open": false,
  "location": {
    "lat": 40.748816,
    "lon": -73.985429
  },
  "signal_strength": -61.4,
  "status": "normal"
}
```

## Supported scenario modes

- `normal` — baseline behavior
- `cold-chain breach` — intermittent temperature excursions
- `unstable battery` — accelerated battery drain + noisier signal
- `offline/recovery` — periodic offline windows and recovery windows
- `multi-device burst` — multiple publications per device each cycle

Scenarios are configured in `scenarios.json`, and devices/profiles are configured in `devices.json`.

## Running safely

From repository root:

```bash
cd /home/runner/work/oncovax-iot-platform/oncovax-iot-platform
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
