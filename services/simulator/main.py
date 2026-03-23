import argparse
import json
import logging
import random
import signal
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Any

import paho.mqtt.client as mqtt


LOGGER = logging.getLogger("oncovax-simulator")
STOP_EVENT = Event()


@dataclass
class DeviceState:
    battery: float
    latitude: float
    longitude: float
    cycle: int = 0


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_payload(
    rng: random.Random,
    device: dict[str, Any],
    state: DeviceState,
    scenario_name: str,
    scenario: dict[str, Any],
) -> dict[str, Any]:
    profile = device["profile"]
    state.cycle += 1

    temperature = profile["temperature_c"]["base"] + rng.uniform(
        -profile["temperature_c"]["jitter"], profile["temperature_c"]["jitter"]
    )
    humidity = profile["humidity_pct"]["base"] + rng.uniform(
        -profile["humidity_pct"]["jitter"], profile["humidity_pct"]["jitter"]
    )
    signal_strength = profile["signal_strength_dbm"]["base"] + rng.uniform(
        -profile["signal_strength_dbm"]["jitter"], profile["signal_strength_dbm"]["jitter"]
    )

    state.battery = clamp(
        state.battery
        - rng.uniform(profile["battery"]["drain_min"], profile["battery"]["drain_max"]),
        profile["battery"]["min"],
        profile["battery"]["max"],
    )

    state.latitude += rng.uniform(-profile["location_drift"]["lat"], profile["location_drift"]["lat"])
    state.longitude += rng.uniform(-profile["location_drift"]["lon"], profile["location_drift"]["lon"])

    door_open = rng.random() < profile["door_open_probability"]
    status = "normal"
    should_publish = True
    burst_count = 1

    if scenario_name == "cold-chain breach":
        breach = rng.random() < scenario.get("breach_probability", 0.3)
        if breach:
            temperature += scenario.get("temperature_increase_c", 8.0)
            status = "cold_chain_breach"
    elif scenario_name == "unstable battery":
        state.battery = clamp(
            state.battery - rng.uniform(*scenario.get("extra_drain_range", [0.3, 1.2])),
            profile["battery"]["min"],
            profile["battery"]["max"],
        )
        signal_strength += rng.uniform(*scenario.get("signal_noise_range", [-15.0, 5.0]))
        status = "unstable_battery" if state.battery < scenario.get("low_battery_threshold", 30.0) else "normal"
    elif scenario_name == "offline/recovery":
        cycle_window = max(1, int(scenario.get("offline_cycles", 5)) + int(scenario.get("recovery_cycles", 5)))
        in_offline = (state.cycle % cycle_window) <= int(scenario.get("offline_cycles", 5))
        if in_offline:
            status = "offline"
            should_publish = scenario.get("publish_offline_status", False)
            signal_strength = -120.0
        else:
            status = "recovery"
            signal_strength += scenario.get("recovery_signal_boost", 8.0)
            state.battery = clamp(
                state.battery + scenario.get("recovery_battery_boost", 1.0),
                profile["battery"]["min"],
                profile["battery"]["max"],
            )
    elif scenario_name == "multi-device burst":
        burst_count = max(1, int(scenario.get("burst_count", 3)))
        status = "burst"

    payload = {
        "timestamp": now_iso(),
        "device_id": device["device_id"],
        "asset_type": device["asset_type"],
        "temperature": round(temperature, 3),
        "humidity": round(clamp(humidity, 0.0, 100.0), 3),
        "battery": round(state.battery, 2),
        "door_open": door_open,
        "location": {"lat": round(state.latitude, 6), "lon": round(state.longitude, 6)},
        "signal_strength": round(signal_strength, 2),
        "status": status,
    }
    return {
        "payload": payload,
        "should_publish": should_publish,
        "burst_count": burst_count,
    }


def handle_signal(signum: int, _frame: Any) -> None:
    LOGGER.info("Received signal %s; shutting down simulator", signum)
    STOP_EVENT.set()


def parse_args() -> argparse.Namespace:
    base_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="OncoVax telemetry simulator")
    parser.add_argument("--mqtt-host", default="localhost")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--mqtt-topic", default="oncovax/telemetry/simulator")
    parser.add_argument("--devices-file", type=Path, default=base_dir / "devices.json")
    parser.add_argument("--scenarios-file", type=Path, default=base_dir / "scenarios.json")
    parser.add_argument("--scenario", default=None, help="Scenario mode to run")
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=None, help="Deterministic random seed")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without MQTT publish")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    args = parse_args()
    rng = random.Random(args.seed)

    devices_config = load_json(args.devices_file)
    scenarios_config = load_json(args.scenarios_file)

    scenario_name = args.scenario or scenarios_config.get("default_scenario", "normal")
    scenario = scenarios_config["scenarios"].get(scenario_name)
    if scenario is None:
        raise ValueError(f"Unknown scenario '{scenario_name}'. Available: {', '.join(scenarios_config['scenarios'])}")

    states: dict[str, DeviceState] = {}
    for device in devices_config["devices"]:
        initial = device["profile"]["battery"].get("initial", 100.0)
        states[device["device_id"]] = DeviceState(
            battery=initial,
            latitude=float(device["location"]["lat"]),
            longitude=float(device["location"]["lon"]),
        )

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if not args.dry_run:
        client.connect(args.mqtt_host, args.mqtt_port, 60)
        client.loop_start()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    LOGGER.info(
        "Starting simulator: scenario=%s devices=%d topic=%s seed=%s dry_run=%s",
        scenario_name,
        len(states),
        args.mqtt_topic,
        args.seed,
        args.dry_run,
    )

    try:
        while not STOP_EVENT.is_set():
            for device in devices_config["devices"]:
                state = states[device["device_id"]]
                out = build_payload(rng, device, state, scenario_name, scenario)
                if not out["should_publish"]:
                    LOGGER.info("device=%s status=offline (skipped publish)", device["device_id"])
                    continue

                for _ in range(out["burst_count"]):
                    burst_payload = dict(out["payload"])
                    burst_payload["timestamp"] = now_iso()
                    payload = json.dumps(burst_payload, separators=(",", ":"))
                    if args.dry_run:
                        LOGGER.info("dry-run payload=%s", payload)
                    else:
                        client.publish(args.mqtt_topic, payload, qos=0)
                        LOGGER.info(
                            "published device=%s status=%s topic=%s",
                            burst_payload["device_id"],
                            burst_payload["status"],
                            args.mqtt_topic,
                        )
            STOP_EVENT.wait(args.interval_seconds)
    finally:
        if not args.dry_run:
            client.loop_stop()
            client.disconnect()
        LOGGER.info("Simulator stopped")


if __name__ == "__main__":
    main()
