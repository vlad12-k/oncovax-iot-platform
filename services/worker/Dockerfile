FROM python:3.12-slim

WORKDIR /app

COPY services/worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/worker /app/services/worker
COPY schemas /app/schemas

ENV MQTT_HOST=mosquitto
ENV MQTT_PORT=1883
ENV MQTT_TOPIC=oncovax/telemetry
ENV INFLUX_URL=http://influxdb:8086
ENV INFLUX_ORG=oncovax
ENV INFLUX_BUCKET=telemetry
ENV INFLUX_TOKEN=dev-token-change-me
ENV MONGO_URI=mongodb://mongodb:27017
ENV MONGO_DB=oncovax
ENV MONGO_COLLECTION=audit_events
ENV TEMP_THRESHOLD=8.0
ENV CONSECUTIVE_BREACH_REQUIRED=1

CMD ["python", "-m", "services.worker.worker"]
