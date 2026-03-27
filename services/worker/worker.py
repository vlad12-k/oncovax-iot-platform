import json
import os
from pathlib import Path
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from jsonschema import validate
from pymongo import MongoClient

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "oncovax/telemetry")
MQTT_TOPICS = os.getenv("MQTT_TOPICS", "")
MQTT_SIMULATOR_COMPAT_TOPIC = os.getenv("MQTT_SIMULATOR_COMPAT_TOPIC", "")

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_ORG = os.getenv("INFLUX_ORG", "oncovax")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "telemetry")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "dev-token-change-me")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "oncovax")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "audit_events")

SCHEMA_PATH = Path(os.getenv("SCHEMA_PATH", "schemas/telemetry.schema.json"))

TEMP_THRESHOLD = float(os.getenv("TEMP_THRESHOLD", "8.0"))
CONSECUTIVE_BREACH_REQUIRED = int(os.getenv("CONSECUTIVE_BREACH_REQUIRED", "1"))
ALERT_DEDUP_COOLDOWN_SECONDS = int(os.getenv("ALERT_DEDUP_COOLDOWN_SECONDS", "300"))

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
breach_state = {}
last_alert_emitted_at = {}
ASSET_TYPE_ALIASES = {
    "vaccine fridge": "coldstorage",
    "clinic freezer": "coldstorage",
    "warehouse cold room": "coldstorage",
    "transport box": "shipment",
}


def normalize_asset_type(asset_type):
    if asset_type is None:
        return asset_type
    normalized = ASSET_TYPE_ALIASES.get(str(asset_type).strip().lower())
    if normalized:
        return normalized
    return asset_type


def build_subscribe_topics():
    topics = [MQTT_TOPIC]
    if MQTT_TOPICS.strip():
        topics.extend([topic.strip() for topic in MQTT_TOPICS.split(",") if topic.strip()])
    if MQTT_SIMULATOR_COMPAT_TOPIC.strip():
        topics.append(MQTT_SIMULATOR_COMPAT_TOPIC.strip())
    deduped = []
    for topic in topics:
        if topic not in deduped:
            deduped.append(topic)
    return deduped


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def build_simulator_note(payload: dict):
    note_fields = {}
    for key in (
        "status",
        "power_state",
        "network_status",
        "compressor_state",
        "site",
        "zone",
        "fleet_group",
        "firmware_version",
        "location",
    ):
        value = payload.get(key)
        if value is not None:
            note_fields[key] = value
    if not note_fields:
        return None
    return json.dumps(note_fields, separators=(",", ":"), sort_keys=True)


def to_canonical_records(payload: dict):
    canonical_required = {"device_id", "asset_type", "ts", "metric", "value", "unit"}
    if canonical_required.issubset(payload.keys()):
        canonical = dict(payload)
        canonical["asset_type"] = normalize_asset_type(canonical["asset_type"])
        return [canonical]

    simulator_required = {"timestamp", "device_id", "asset_type"}
    if not simulator_required.issubset(payload.keys()):
        raise ValueError("Unsupported telemetry payload format")

    note = build_simulator_note(payload)
    asset_type = normalize_asset_type(payload["asset_type"])
    metric_defs = (
        ("temperature", "temperature", "C", float),
        ("humidity", "humidity", "%", float),
        ("battery", "battery", "%", float),
        ("door_open", "door_open", "state", lambda value: 1.0 if bool(value) else 0.0),
        ("open_duration_seconds", "open_duration_seconds", "seconds", float),
        ("signal_strength", "signal_strength", "dBm", float),
        ("ambient_temperature", "ambient_temperature", "C", float),
        ("setpoint_temperature", "setpoint_temperature", "C", float),
    )

    records = []
    for source_key, metric, unit, converter in metric_defs:
        if source_key not in payload:
            continue
        raw_value = payload[source_key]
        if raw_value is None:
            continue
        record = {
            "device_id": payload["device_id"],
            "asset_type": asset_type,
            "ts": payload["timestamp"],
            "metric": metric,
            "value": converter(raw_value),
            "unit": unit,
        }
        if note is not None:
            record["note"] = note
        records.append(record)

    if not records:
        raise ValueError("Simulator payload does not contain supported metric fields")

    return records


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

    ts = data.get("ts")
    if ts:
        p = p.time(ts)

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

    if "ts" in alert:
        p = p.time(alert["ts"])

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)


def write_audit_record(audit_collection, alert: dict):
    audit_doc = {
        "alert_id": f"{alert['device_id']}-{alert['metric']}-{alert['ts']}",
        "event_type": "excursion_alert",
        "time": alert["ts"],
        "device_id": alert["device_id"],
        "asset_type": alert["asset_type"],
        "metric": alert["metric"],
        "value": alert["value"],
        "threshold": alert["threshold"],
        "status": alert["status"],
        "consecutive_breach_count": alert["consecutive_breach_count"],
        "acknowledged": False,
        "acknowledged_by": None,
        "incident_note": None,
        "message": alert["message"],
    }
    audit_collection.insert_one(audit_doc)


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
        breach_state.pop(key, None)
        return None

    count = breach_state[key]
    if count == CONSECUTIVE_BREACH_REQUIRED:
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


def should_emit_alert(alert: dict):
    if ALERT_DEDUP_COOLDOWN_SECONDS <= 0:
        return True

    key = (alert["device_id"], alert["metric"])
    now_ts = datetime.now(timezone.utc).timestamp()
    last_emitted = last_alert_emitted_at.get(key)

    if last_emitted is not None and (now_ts - last_emitted) < ALERT_DEDUP_COOLDOWN_SECONDS:
        return False

    last_alert_emitted_at[key] = now_ts
    return True


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[worker] connected to mqtt rc={reason_code}")
    subscribe_topics = userdata["subscribe_topics"]
    for topic in subscribe_topics:
        client.subscribe(topic)
        print(f"[worker] subscribed topic={topic}")


def on_message(client, userdata, msg):
    write_api = userdata["write_api"]
    audit_collection = userdata["audit_collection"]

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        records = to_canonical_records(payload)
        for record in records:
            validate(instance=record, schema=schema)
            write_telemetry_point(write_api, record)
            print(f"[worker] wrote telemetry: {record}")

            alert = evaluate_excursion(record)
            if alert:
                if not should_emit_alert(alert):
                    print(
                        f"[alert] suppressed duplicate for "
                        f"{alert['device_id']}:{alert['metric']} "
                        f"(cooldown={ALERT_DEDUP_COOLDOWN_SECONDS}s)"
                    )
                    continue
                write_alert_point(write_api, alert)
                write_audit_record(audit_collection, alert)
                print(f"[alert] {alert}")
                print(f"[audit] stored alert_id={alert['device_id']}-{alert['metric']}-{alert['ts']}")

    except Exception as e:
        print(f"[worker] error: {e}")


def main():
    subscribe_topics = build_subscribe_topics()
    print(f"[worker] mqtt://{MQTT_HOST}:{MQTT_PORT} topics={subscribe_topics}")
    print(f"[worker] influx: {INFLUX_URL} org={INFLUX_ORG} bucket={INFLUX_BUCKET}")
    print(f"[worker] mongo: {MONGO_URI} db={MONGO_DB} collection={MONGO_COLLECTION}")
    print(
        f"[worker] excursion rule: temperature > {TEMP_THRESHOLD} "
        f"for {CONSECUTIVE_BREACH_REQUIRED} consecutive readings"
    )
    print(f"[worker] alert dedup cooldown: {ALERT_DEDUP_COOLDOWN_SECONDS}s")

    influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = influx.write_api(write_options=SYNCHRONOUS)

    mongo_client = MongoClient(MONGO_URI)
    audit_collection = mongo_client[MONGO_DB][MONGO_COLLECTION]

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.user_data_set({
        "write_api": write_api,
        "audit_collection": audit_collection,
        "subscribe_topics": subscribe_topics,
    })
    client.on_connect = on_connect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main()
