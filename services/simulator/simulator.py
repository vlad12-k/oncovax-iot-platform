import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "oncovax/telemetry")

DEVICE_ID = os.getenv("DEVICE_ID", "sim-001")
ASSET_TYPE = os.getenv("ASSET_TYPE", "coldstorage")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def make_reading(metric: str, unit: str, base: float, jitter: float) -> dict:
    return {
        "device_id": DEVICE_ID,
        "asset_type": ASSET_TYPE,
        "ts": now_iso(),
        "metric": metric,
        "value": round(base + random.uniform(-jitter, jitter), 3),
        "unit": unit,
    }

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    print(f"[sim] publishing to mqtt://{MQTT_HOST}:{MQTT_PORT} topic={MQTT_TOPIC}")

    while True:
        msg = make_reading("temperature", "C", base=4.0, jitter=0.2)

        # inject an excursion spike (demo)
        if random.random() < 0.02:
            msg["value"] = 10.5
            msg["note"] = "excursion_injected"

        payload = json.dumps(msg)
        client.publish(MQTT_TOPIC, payload, qos=0)
        print("[sim]", payload)
        time.sleep(1)

if __name__ == "__main__":
    main()
