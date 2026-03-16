import json
import os
from pathlib import Path
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from jsonschema import validate

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "oncovax/telemetry")

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_ORG = os.getenv("INFLUX_ORG", "oncovax")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "telemetry")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "dev-token-change-me")

SCHEMA_PATH = Path(os.getenv("SCHEMA_PATH", "schemas/telemetry.schema.json"))

TEMP_THRESHOLD = float(os.getenv("TEMP_THRESHOLD", "8.0"))
CONSECUTIVE_BREACH_REQUIRED = int(os.getenv("CONSECUTIVE_BREACH_REQUIRED", "2"))

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

breach_state = {}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def write_telemetry_point(write_api, data: dict):
    p = (
        Point("telemetry")
        .tag("device_id", data["device_id"])
        .tag("asset_type", data["asset_type"])
        .tag("metric", data["metric"])
        .field("value", float(data["value"]))
        .field("unit", data["unit"])
    )

    if "note" in data:
        p = p.field("note", str(data["note"]))

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)


def write_alert_point(write_api, alert: dict):
    p = (
        Point("alerts")
        .tag("device_id", alert["device_id"])
        .tag("asset_type", alert["asset_type"])
        .tag("metric", alert["metric"])
        .tag("status", alert["status"])
        .field("threshold", float(alert["threshold"]))
        .field("value", float(alert["value"]))
        .field("consecutive_breach_count", int(alert["consecutive_breach_count"]))
        .field("message", alert["message"])
    )
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)


def evaluate_excursion(data: dict):
    metric = data.get("metric")
    if metric != "temperature":
        return None

    device_id = data["device_id"]
    key = (device_id, metric)
    value = float(data["value"])

    if value > TEMP_THRESHOLD:
        breach_state[key] = breach_state.get(key, 0) + 1
    else:
        breach_state[key] = 0
        return None

    count = breach_state[key]
    if count >= CONSECUTIVE_BREACH_REQUIRED:
        return {
            "ts": now_iso(),
            "device_id": data["device_id"],
            "asset_type": data["asset_type"],
            "metric": metric,
            "threshold": TEMP_THRESHOLD,
            "value": value,
            "status": "active",
            "consecutive_breach_count": count,
            "message": f"Excursion detected: {metric} > {TEMP_THRESHOLD} for {count} consecutive readings",
        }

    return None


def on_message(client, userdata, msg):
    write_api = userdata["write_api"]

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        validate(instance=payload, schema=schema)

        write_telemetry_point(write_api, payload)
        print(f"[worker] wrote telemetry: {payload}")

        alert = evaluate_excursion(payload)
        if alert:
            write_alert_point(write_api, alert)
            print(f"[alert] {alert}")

    except Exception as e:
        print(f"[worker] error: {e}")


def main():
    print(f"[worker] mqtt://{MQTT_HOST}:{MQTT_PORT} topic={MQTT_TOPIC}")
    print(f"[worker] influx: {INFLUX_URL} org={INFLUX_ORG} bucket={INFLUX_BUCKET}")
    print(
        f"[worker] excursion rule: temperature > {TEMP_THRESHOLD} "
        f"for {CONSECUTIVE_BREACH_REQUIRED} consecutive readings"
    )

    influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.user_data_set({"write_api": write_api})
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()


if __name__ == "__main__":
    main()
