FROM python:3.12-slim

WORKDIR /app

COPY services/orchestration_adapter/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/orchestration_adapter/main.py /app/main.py

CMD ["python", "/app/main.py"]
