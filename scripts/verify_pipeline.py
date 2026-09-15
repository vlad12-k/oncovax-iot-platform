"""Exercise local MQTT -> InfluxDB/MongoDB -> API acknowledgement with a unique probe.

Requires the development Compose stack. The probe remains as identifiable validation
history in local stores; no existing records or volumes are removed.
"""
import json
import os
import time
import uuid
from datetime import datetime, timezone

import httpx
import paho.mqtt.publish as publish
from influxdb_client import InfluxDBClient


def main():
    device = 'verification-' + uuid.uuid4().hex[:12]
    payload = dict(device_id=device, asset_type='coldstorage',
                   ts=datetime.now(timezone.utc).isoformat(), metric='temperature', value=99.0, unit='C')
    with httpx.Client(base_url='http://localhost:8000', timeout=10) as api, InfluxDBClient(
        url='http://localhost:8086', token='dev-token-change-me', org='oncovax', timeout=10000
    ) as influx:
        deadline = time.monotonic() + 60
        alert = None
        while time.monotonic() < deadline:
            publish.single('oncovax/telemetry', json.dumps(payload), hostname='localhost', port=1883)
            response = api.get('/alerts', params={'limit': 200})
            response.raise_for_status()
            alert = next((item for item in response.json()['items'] if item['device_id'] == device), None)
            if alert:
                break
            time.sleep(2)
        if not alert:
            raise RuntimeError(f'No persisted alert for {device} within 60 seconds')
        query = ('from(bucket: "telemetry") |> range(start: -5m) '
                 '|> filter(fn: (r) => r._measurement == "telemetry" and '
                 f'r.device_id == "{device}" and r._field == "value") |> limit(n: 1)')
        if not influx.query_api().query(query):
            raise RuntimeError(f'No InfluxDB telemetry for {device}')
        response = api.post(f'/alerts/{alert["alert_id"]}/acknowledge',
                            json={'acknowledged_by': 'local-verification', 'incident_note': 'Automated pipeline check'})
        response.raise_for_status()
        item = response.json()['item']
        if not item['acknowledged'] or item['acknowledged_by'] != 'local-verification':
            raise RuntimeError('Acknowledgement round trip failed')
        print(f'PASS: {device}: MQTT ingestion, InfluxDB, persisted alert and API acknowledgement')


if __name__ == '__main__':
    main()
