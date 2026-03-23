import argparse
import json
import logging
import os
import random
import signal
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Any

import paho.mqtt.client as mqtt

from runtime_control import RuntimeController


LOGGER = logging.getLogger("oncovax-simulator")
STOP_EVENT = Event()
DEMO_PROFILE_DOOR_CYCLE = 2
DEMO_PROFILE_TEMP_SPIKE_CYCLE = 3
DEMO_PROFILE_TEMP_SPIKE_C = 2.0
DEMO_PROFILE_MIN_BURST_COUNT = 2
DEFAULT_RUNTIME_CONTROL_TOPIC = "oncovax/demo/internal/simulator/runtime/control"


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


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid float value") from exc


def _env_int_optional(name: str) -> int | None:
    raw = os.getenv(name)
    if raw in (None, ""):
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid integer value") from exc


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


def apply_runtime_override(out: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    event_type = override["event_type"]
    payload = out["payload"]

    if event_type == "burst_pulse":
        params = override.get("params", {})
        burst_count = params.get("burst_count", 5)
        if isinstance(burst_count, int) and burst_count > 0:
            out["burst_count"] = max(out["burst_count"], burst_count)
        payload["status"] = "burst"
    elif event_type == "breach_pulse":
        params = override.get("params", {})
        temperature_increase_c = params.get("temperature_increase_c", 8.0)
        if isinstance(temperature_increase_c, (int, float)):
            payload["temperature"] = round(float(payload["temperature"]) + float(temperature_increase_c), 3)
        payload["status"] = "cold_chain_breach"
    elif event_type == "offline_pulse":
        payload["network_status"] = "offline"
        payload["signal_strength"] = -120.0
        payload["status"] = "offline"
        out["should_publish"] = True

    return out


def parse_args() -> argparse.Namespace:
    base_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="OncoVax telemetry simulator")
    parser.add_argument("--mqtt-host", default=os.getenv("MQTT_HOST", "localhost"))
    parser.add_argument("--mqtt-port", type=int, default=int(os.getenv("MQTT_PORT", "1883")))
    parser.add_argument("--mqtt-topic", default=os.getenv("MQTT_TOPIC", "oncovax/telemetry/simulator"))
    parser.add_argument("--devices-file", type=Path, default=base_dir / "devices.json")
    parser.add_argument("--scenarios-file", type=Path, default=base_dir / "scenarios.json")
    parser.add_argument("--scenario", default=os.getenv("SIM_SCENARIO") or None, help="Scenario mode to run")
    parser.add_argument(
        "--profile",
        choices=["standard", "demo"],
        default=(os.getenv("SIM_PROFILE") or "standard"),
        help="Use demo profile to force visible events in short windows",
    )
    parser.add_argument("--interval-seconds", type=float, default=_env_float("SIM_INTERVAL_SECONDS", 1.0))
    parser.add_argument(
        "--seed",
        type=int,
        default=_env_int_optional("SIM_SEED"),
        help="Deterministic random seed",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without MQTT publish")
    parser.add_argument(
        "--runtime-control-topic",
        default=os.getenv("SIM_RUNTIME_CONTROL_TOPIC", DEFAULT_RUNTIME_CONTROL_TOPIC),
        help="Internal runtime-control topic consumed by simulator",
    )
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
    startup_scenario = args.scenario or (demo_default_scenario if args.profile == "demo" else default_scenario)
    startup_profile = args.profile
    controller = RuntimeController(startup_scenario=startup_scenario, startup_profile=startup_profile)

    scenario = scenarios_config["scenarios"].get(startup_scenario)
    if scenario is None:
        available = ", ".join(sorted(scenarios_config["scenarios"].keys()))
        raise ValueError(f"Unknown scenario '{startup_scenario}'. Available: {available}")

    states: dict[str, DeviceState] = {}
    for device in devices_config["devices"]:
        initial = device["profile"]["battery"].get("initial", 100.0)
        states[device["device_id"]] = DeviceState(
            battery=initial,
            latitude=float(device["location"]["lat"]),
            longitude=float(device["location"]["lon"]),
        )

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_control_message(_client: mqtt.Client, _userdata: Any, msg: Any) -> None:
        try:
            body = json.loads(msg.payload.decode("utf-8"))
            action = body.get("action")
            if action == "set_scenario":
                scenario_name = body.get("scenario")
                if scenario_name not in scenarios_config["scenarios"]:
                    LOGGER.warning("Ignoring unknown scenario in runtime control: %s", scenario_name)
                    return
                controller.set_scenario(scenario_name)
                LOGGER.info("runtime control applied: set_scenario=%s", scenario_name)
            elif action == "set_profile":
                profile = body.get("profile")
                if profile not in {"standard", "demo"}:
                    LOGGER.warning("Ignoring unknown profile in runtime control: %s", profile)
                    return
                controller.set_profile(profile)
                LOGGER.info("runtime control applied: set_profile=%s", profile)
            elif action == "apply_temporary_override":
                event_type = body.get("event_type")
                duration_cycles = body.get("duration_cycles")
                params = body.get("params", {})
                if not isinstance(event_type, str) or not isinstance(duration_cycles, int):
                    LOGGER.warning("Invalid override payload: %s", body)
                    return
                controller.apply_temporary_override(
                    event_type, duration_cycles, params if isinstance(params, dict) else {}
                )
                LOGGER.info(
                    "runtime control applied: temporary_override event_type=%s duration_cycles=%s",
                    event_type,
                    duration_cycles,
                )
            elif action == "reset_runtime":
                controller.reset_runtime()
                LOGGER.info("runtime control applied: reset_runtime")
            else:
                LOGGER.warning("Ignoring unsupported runtime action=%s", action)
        except Exception as exc:
            LOGGER.warning("Failed to process runtime control message: %s", exc)

    client.on_message = on_control_message
    if not args.dry_run:
        client.connect(args.mqtt_host, args.mqtt_port, 60)
        client.subscribe(args.runtime_control_topic, qos=0)
        client.loop_start()
        LOGGER.info("subscribed runtime control topic=%s", args.runtime_control_topic)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    LOGGER.info(
        "Starting simulator: scenario=%s profile=%s devices=%d topic=%s seed=%s dry_run=%s",
        startup_scenario,
        startup_profile,
        len(states),
        args.mqtt_topic,
        args.seed,
        args.dry_run,
    )

    try:
        while not STOP_EVENT.is_set():
            runtime_state = controller.snapshot()
            scenario_name = runtime_state["scenario"]
            profile_name = runtime_state["profile"]
            scenario = scenarios_config["scenarios"].get(scenario_name)
            if scenario is None:
                LOGGER.warning("runtime scenario not found; using startup scenario=%s", startup_scenario)
                scenario_name = startup_scenario
                scenario = scenarios_config["scenarios"][scenario_name]
            for device in devices_config["devices"]:
                state = states[device["device_id"]]
                out = build_payload(rng, device, state, scenario_name, scenario, profile_name)
                if runtime_state["temporary_override"] is not None:
                    out = apply_runtime_override(out, runtime_state["temporary_override"])
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
            controller.tick_cycle()
            STOP_EVENT.wait(args.interval_seconds)
    finally:
        if not args.dry_run:
            client.loop_stop()
            client.disconnect()
        LOGGER.info("Simulator stopped")


if __name__ == "__main__":
    main()
