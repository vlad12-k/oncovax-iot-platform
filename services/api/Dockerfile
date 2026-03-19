FROM python:3.12-slim

WORKDIR /app

COPY services/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/api /app/services/api
COPY services/web /app/services/web

ENV MONGO_URI=mongodb://mongodb:27017
ENV MONGO_DB=oncovax
ENV MONGO_COLLECTION=audit_events

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
