import json
import os
from pathlib import Path

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

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

def write_point(write_api, data: dict):
    p = (
        Point("telemetry")
        .tag("device_id", str(data.get("device_id", "unknown")))
        .tag("asset_type", str(data.get("asset_type", "unknown")))
        .tag("metric", str(data.get("metric", "unknown")))
        .field("value", float(data["value"]))
    )
    if "ts" in data:
        p = p.time(data["ts"])
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)

def on_message(write_api):
    def _handler(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
            validate(instance=data, schema=schema)
            write_point(write_api, data)
            print("[worker] wrote:", data)
        except Exception as e:
            print("[worker] dropped:", e)
    return _handler

def main():
    print(f"[worker] mqtt://{MQTT_HOST}:{MQTT_PORT} topic={MQTT_TOPIC}")
    print(f"[worker] influx: {INFLUX_URL} org={INFLUX_ORG} bucket={INFLUX_BUCKET}")

    influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message(write_api)
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()

if __name__ == "__main__":
    main()
