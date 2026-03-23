import argparse
import json
import logging
import random
import signal
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Any

import paho.mqtt.client as mqtt


LOGGER = logging.getLogger("oncovax-simulator")
STOP_EVENT = Event()
DEMO_PROFILE_DOOR_CYCLE = 2
DEMO_PROFILE_TEMP_SPIKE_CYCLE = 3
DEMO_PROFILE_TEMP_SPIKE_C = 2.0
DEMO_PROFILE_MIN_BURST_COUNT = 2


@dataclass
class DeviceState:
    battery: float
    latitude: float
    longitude: float
    cycle: int = 0
    open_duration_seconds: int = 0
    door_incident_remaining: int = 0


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _door_open_next_duration(rng: random.Random, state: DeviceState, is_open: bool) -> int:
    if is_open:
        if state.open_duration_seconds <= 0:
            state.open_duration_seconds = int(rng.uniform(8.0, 60.0))
        else:
            state.open_duration_seconds += int(rng.uniform(5.0, 20.0))
    else:
        state.open_duration_seconds = 0
    return state.open_duration_seconds


def _compressor_state(asset_type: str, power_state: str, temperature: float, setpoint: float) -> str | None:
    if asset_type == "transport box":
        return None
    if power_state != "on":
        return "off"
    if temperature > (setpoint + 0.5):
        return "on"
    if temperature < (setpoint - 0.4):
        return "standby"
    return "cycling"


def build_payload(
    rng: random.Random,
    device: dict[str, Any],
    state: DeviceState,
    scenario_name: str,
    scenario: dict[str, Any],
    profile_name: str,
) -> dict[str, Any]:
    profile = device["profile"]
    state.cycle += 1

    setpoint_temperature = float(
        device.get("setpoint_temperature_c", profile.get("temperature_c", {}).get("base", 4.0))
    )
    ambient_temperature = profile["ambient_temperature_c"]["base"] + rng.uniform(
        -profile["ambient_temperature_c"]["jitter"],
        profile["ambient_temperature_c"]["jitter"],
    )
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
    power_state = "on"
    network_status = "online"
    should_publish = True
    burst_count = 1

    if scenario_name == "cold-chain breach":
        breach = rng.random() < scenario.get("breach_probability", 0.3)
        if breach:
            temperature += scenario.get("temperature_increase_c", 8.0)
            ambient_temperature += scenario.get("ambient_increase_c", 2.0)
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
        offline_cycles = int(scenario.get("offline_cycles", 5))
        recovery_cycles = int(scenario.get("recovery_cycles", 5))
        cycle_window = max(1, offline_cycles + recovery_cycles)
        in_offline = (state.cycle % cycle_window) < offline_cycles
        if in_offline:
            status = "offline"
            network_status = "offline"
            should_publish = scenario.get("publish_offline_status", False)
            signal_strength = -120.0
        else:
            status = "recovery"
            network_status = "recovering"
            signal_strength += scenario.get("recovery_signal_boost", 8.0)
            state.battery = clamp(
                state.battery + scenario.get("recovery_battery_boost", 1.0),
                profile["battery"]["min"],
                profile["battery"]["max"],
            )
    elif scenario_name == "multi-device burst":
        burst_count = max(1, int(scenario.get("burst_count", 3)))
        status = "burst"
    elif scenario_name == "transport instability":
        if device["asset_type"] == "transport box":
            temperature += rng.uniform(*scenario.get("temperature_swing_range", [-3.0, 5.0]))
            humidity += rng.uniform(*scenario.get("humidity_swing_range", [-8.0, 12.0]))
            signal_strength += rng.uniform(*scenario.get("signal_noise_range", [-20.0, 8.0]))
            door_open = rng.random() < scenario.get("door_open_probability", 0.35)
            status = "transport_instability"
        else:
            status = "normal"
    elif scenario_name == "prolonged door-open incident":
        if state.door_incident_remaining <= 0 and rng.random() < scenario.get("incident_probability", 0.2):
            state.door_incident_remaining = int(rng.uniform(*scenario.get("incident_cycles_range", [3, 7])))
        if state.door_incident_remaining > 0:
            state.door_incident_remaining -= 1
            door_open = True
            temperature += scenario.get("temperature_rise_c", 2.8)
            humidity += scenario.get("humidity_rise_pct", 6.5)
            status = "door_open_incident"
    elif scenario_name == "repeated breach pattern":
        breach_cycles = int(scenario.get("breach_cycles", 2))
        normal_cycles = int(scenario.get("normal_cycles", 3))
        pattern_window = max(1, breach_cycles + normal_cycles)
        in_breach = (state.cycle % pattern_window) < breach_cycles
        if in_breach:
            temperature += scenario.get("temperature_increase_c", 7.5)
            ambient_temperature += scenario.get("ambient_increase_c", 1.8)
            status = "repeated_breach"
    elif scenario_name == "demo-friendly":
        burst_count = max(2, int(scenario.get("burst_count", 3)))
        door_cycle = max(1, int(scenario.get("door_open_every_n_cycles", 2)))
        breach_cycle = max(1, int(scenario.get("breach_every_n_cycles", 3)))
        offline_cycle = max(1, int(scenario.get("offline_every_n_cycles", 5)))
        battery_cycle = max(1, int(scenario.get("battery_drop_every_n_cycles", 4)))

        if state.cycle % door_cycle == 0:
            door_open = True
            status = "door_open_incident"
            temperature += scenario.get("door_event_temp_rise_c", 2.0)
        if state.cycle % breach_cycle == 0:
            temperature += scenario.get("breach_temp_increase_c", 6.0)
            status = "cold_chain_breach"
        if state.cycle % battery_cycle == 0:
            state.battery = clamp(
                state.battery - scenario.get("battery_drop_pct", 4.0),
                profile["battery"]["min"],
                profile["battery"]["max"],
            )
            status = "unstable_battery"
        if state.cycle % offline_cycle == 0:
            network_status = "offline"
            signal_strength = -120.0
            status = "offline"
            should_publish = scenario.get("publish_offline_status", True)

    if rng.random() < profile.get("power_loss_probability", 0.0):
        power_state = "outage"
        status = "power_loss"
        temperature += rng.uniform(1.0, 2.5)

    if network_status == "online" and rng.random() < profile.get("network_drop_probability", 0.0):
        network_status = "intermittent"
        signal_strength += rng.uniform(-12.0, -4.0)

    if profile_name == "demo":
        # Guarantee visible events in short windows regardless of selected scenario.
        if state.cycle % DEMO_PROFILE_DOOR_CYCLE == 0:
            door_open = True
            status = status if status != "normal" else "demo_door_activity"
        if state.cycle % DEMO_PROFILE_TEMP_SPIKE_CYCLE == 0:
            temperature += DEMO_PROFILE_TEMP_SPIKE_C
            status = status if status != "normal" else "demo_temp_spike"
        burst_count = max(burst_count, DEMO_PROFILE_MIN_BURST_COUNT)

    open_duration_seconds = _door_open_next_duration(rng, state, door_open)
    compressor_state = _compressor_state(device["asset_type"], power_state, temperature, setpoint_temperature)

    payload: dict[str, Any] = {
        "timestamp": now_iso(),
        "device_id": device["device_id"],
        "asset_type": device["asset_type"],
        "site": device.get("site"),
        "zone": device.get("zone"),
        "fleet_group": device.get("fleet_group"),
        "firmware_version": device.get("firmware_version"),
        "temperature": round(temperature, 3),
        "humidity": round(clamp(humidity, 0.0, 100.0), 3),
        "battery": round(state.battery, 2),
        "door_open": door_open,
        "open_duration_seconds": open_duration_seconds,
        "signal_strength": round(signal_strength, 2),
        "status": status,
        "ambient_temperature": round(ambient_temperature, 3),
        "setpoint_temperature": round(setpoint_temperature, 3),
        "power_state": power_state,
        "network_status": network_status,
        "location": {"lat": round(state.latitude, 6), "lon": round(state.longitude, 6)},
    }

    if compressor_state is not None:
        payload["compressor_state"] = compressor_state

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
    parser.add_argument(
        "--profile",
        choices=["standard", "demo"],
        default="standard",
        help="Use demo profile to force visible events in short windows",
    )
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

    default_scenario = scenarios_config.get("default_scenario", "normal")
    demo_default_scenario = scenarios_config.get("demo_default_scenario", "demo-friendly")
    scenario_name = args.scenario or (demo_default_scenario if args.profile == "demo" else default_scenario)

    scenario = scenarios_config["scenarios"].get(scenario_name)
    if scenario is None:
        available = ", ".join(sorted(scenarios_config["scenarios"].keys()))
        raise ValueError(f"Unknown scenario '{scenario_name}'. Available: {available}")

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
        "Starting simulator: scenario=%s profile=%s devices=%d topic=%s seed=%s dry_run=%s",
        scenario_name,
        args.profile,
        len(states),
        args.mqtt_topic,
        args.seed,
        args.dry_run,
    )

    try:
        while not STOP_EVENT.is_set():
            for device in devices_config["devices"]:
                state = states[device["device_id"]]
                out = build_payload(rng, device, state, scenario_name, scenario, args.profile)
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
