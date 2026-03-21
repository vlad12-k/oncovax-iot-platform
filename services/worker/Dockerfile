FROM python:3.12-slim

WORKDIR /app

COPY services/worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/worker /app/services/worker
COPY schemas /app/schemas

# Runtime configuration must be supplied via env_file or environment at deploy time.
# The worker code already has safe local-dev defaults via os.getenv().
# See infra/.env.example for the full list of required environment variables.

CMD ["python", "-m", "services.worker.worker"]
