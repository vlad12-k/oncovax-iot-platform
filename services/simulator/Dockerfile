FROM python:3.12-slim

WORKDIR /app

COPY services/simulator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/simulator/main.py /app/main.py
COPY services/simulator/runtime_control.py /app/runtime_control.py
COPY services/simulator/devices.json /app/devices.json
COPY services/simulator/scenarios.json /app/scenarios.json

CMD ["python", "/app/main.py"]
