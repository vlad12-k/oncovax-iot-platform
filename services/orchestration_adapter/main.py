from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import paho.mqtt.client as mqtt


LOGGER = logging.getLogger("oncovax-orchestration-adapter")

CONTROL_TOPICS = {
    "scenario/select": "oncovax/demo/control/scenario/select",
    "mode/set": "oncovax/demo/control/mode/set",
    "event/trigger": "oncovax/demo/control/event/trigger",
}
STATUS_TOPIC = os.getenv("ORCHESTRATION_STATUS_TOPIC", "oncovax/demo/orchestration/status")
INTERNAL_RUNTIME_TOPIC = os.getenv(
    "SIM_RUNTIME_CONTROL_TOPIC", "oncovax/demo/internal/simulator/runtime/control"
)
SUPPORTED_EVENT_TYPES = {"burst_pulse", "breach_pulse", "offline_pulse", "reset_runtime"}
DEFAULT_DURATION_CYCLES = {
    "burst_pulse": 3,
    "breach_pulse": 3,
    "offline_pulse": 3,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        raise ValueError("payload must be JSON object")
    return payload


def _missing_fields(body: dict[str, Any], required: list[str]) -> list[str]:
    return [key for key in required if body.get(key) in (None, "")]


def _base_status(source_topic: str, command_type: str, status: str, command_id: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "contract_version": "1.0",
        "status": status,
        "source_topic": source_topic,
        "command_type": command_type,
        "received_at": now_iso(),
    }
    if command_id:
        payload["command_id"] = command_id
    return payload


def _extract_duration(body: dict[str, Any], event_type: str) -> int:
    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    raw = body.get("duration_cycles", data.get("duration_cycles", DEFAULT_DURATION_CYCLES.get(event_type, 0)))
    if event_type == "reset_runtime":
        return 0
    if not isinstance(raw, int) or raw <= 0:
        raise ValueError("duration_cycles must be a positive integer")
    return raw


def validate_and_map(source_topic: str, payload: Any) -> tuple[dict[str, Any], dict[str, Any] | None]:
    command_type = next((key for key, topic in CONTROL_TOPICS.items() if topic == source_topic), "unknown")
    try:
        body = normalize_payload(payload)
    except Exception as exc:
        status = _base_status(source_topic, command_type, "rejected")
        status["reason"] = str(exc)
        return status, None

    required = ["command_id", "issued_at"]
    missing = _missing_fields(body, required)
    if missing:
        status = _base_status(source_topic, command_type, "rejected", body.get("command_id"))
        status["reason"] = f"missing fields: {', '.join(missing)}"
        return status, None

    if source_topic == CONTROL_TOPICS["scenario/select"]:
        if not isinstance(body.get("scenario"), str) or not body["scenario"].strip():
            status = _base_status(source_topic, "scenario/select", "rejected", body["command_id"])
            status["reason"] = "scenario must be non-empty string"
            return status, None
        mapped = {
            "action": "set_scenario",
            "command_id": body["command_id"],
            "issued_at": body["issued_at"],
            "scenario": body["scenario"],
        }
    elif source_topic == CONTROL_TOPICS["mode/set"]:
        if not isinstance(body.get("enabled"), bool):
            status = _base_status(source_topic, "mode/set", "rejected", body["command_id"])
            status["reason"] = "enabled must be boolean"
            return status, None
        mapped = {
            "action": "set_profile",
            "command_id": body["command_id"],
            "issued_at": body["issued_at"],
            "profile": "demo" if body["enabled"] else "standard",
            "enabled": body["enabled"],
        }
    elif source_topic == CONTROL_TOPICS["event/trigger"]:
        event_type = body.get("event_type")
        if event_type not in SUPPORTED_EVENT_TYPES:
            status = _base_status(source_topic, "event/trigger", "rejected", body["command_id"])
            status["reason"] = f"event_type must be one of: {', '.join(sorted(SUPPORTED_EVENT_TYPES))}"
            return status, None

        if event_type == "reset_runtime":
            mapped = {
                "action": "reset_runtime",
                "command_id": body["command_id"],
                "issued_at": body["issued_at"],
                "event_type": event_type,
            }
        else:
            try:
                duration_cycles = _extract_duration(body, event_type)
            except ValueError as exc:
                status = _base_status(source_topic, "event/trigger", "rejected", body["command_id"])
                status["reason"] = str(exc)
                return status, None

            mapped = {
                "action": "apply_temporary_override",
                "command_id": body["command_id"],
                "issued_at": body["issued_at"],
                "event_type": event_type,
                "duration_cycles": duration_cycles,
                "params": body.get("data", {}),
            }
    else:
        status = _base_status(source_topic, command_type, "rejected", body["command_id"])
        status["reason"] = "unsupported control topic"
        return status, None

    accepted = _base_status(source_topic, command_type, "accepted", body["command_id"])
    accepted["issued_at"] = body["issued_at"]
    return accepted, mapped


def on_connect(client: mqtt.Client, _userdata: Any, _flags: Any, reason_code: int, _properties: Any) -> None:
    if reason_code != 0:
        LOGGER.error("MQTT connect failed reason_code=%s", reason_code)
        return
    for topic in CONTROL_TOPICS.values():
        client.subscribe(topic, qos=0)
        LOGGER.info("subscribed topic=%s", topic)


def on_message(client: mqtt.Client, _userdata: Any, msg: Any) -> None:
    status_payload, mapped_payload = validate_and_map(msg.topic, msg.payload)
    client.publish(STATUS_TOPIC, json.dumps(status_payload, separators=(",", ":")), qos=0)
    if mapped_payload is not None:
        client.publish(INTERNAL_RUNTIME_TOPIC, json.dumps(mapped_payload, separators=(",", ":")), qos=0)
        LOGGER.info("mapped command topic=%s action=%s", msg.topic, mapped_payload["action"])
    else:
        LOGGER.info("rejected command topic=%s reason=%s", msg.topic, status_payload.get("reason"))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    mqtt_host = os.getenv("MQTT_HOST", "localhost")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    LOGGER.info("starting orchestration adapter mqtt://%s:%s", mqtt_host, mqtt_port)
    LOGGER.info("status_topic=%s internal_runtime_topic=%s", STATUS_TOPIC, INTERNAL_RUNTIME_TOPIC)

    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
