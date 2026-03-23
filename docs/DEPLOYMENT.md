# Deployment Guide – OncoVax IoT Monitoring Platform

## Overview

This guide covers three distinct deployment modes:

1. **Local full-stack development** (all services on one machine via `docker-compose.dev.yml`).
2. **Hosted baseline** on a DigitalOcean Droplet with **MongoDB Atlas** for audit data (API + dashboard hosted, Atlas-backed persistence).
3. **Production-like deployment** using `docker-compose.prod.yml` with **nginx + TLS scaffold**.

Each mode is intentionally scoped; none represent a fully hardened, audited production deployment.

---

## Prerequisites

- Docker and Docker Compose installed
- Git
- `curl` available for smoke tests
- For Atlas: a MongoDB Atlas cluster and connection string
- For hosted baseline: a DigitalOcean Droplet (Ubuntu 22.04 LTS recommended) with Docker installed

---

## 1) Local Full-Stack Development (Docker Compose Dev)

This mode runs **all services locally**, including MongoDB and InfluxDB.

### 1. Clone the repository

```bash
git clone https://github.com/vlad12-k/oncovax-iot-platform.git
cd oncovax-iot-platform
```

### 2. Configure environment

```bash
cp infra/.env.example infra/.env
# Edit infra/.env and fill in real values
```

Key variables to set:
- `INFLUX_TOKEN` – a secure random string (generate with `openssl rand -hex 32`)
- `DOCKER_INFLUXDB_INIT_PASSWORD` – InfluxDB admin password
- `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` – must match `INFLUX_TOKEN`
- `GF_SECURITY_ADMIN_PASSWORD` – Grafana admin password

### 3. Start the dev stack

```bash
docker compose -f infra/docker-compose.dev.yml up -d --build
```

This starts: Mosquitto, InfluxDB, MongoDB, FastAPI, Node-RED, Grafana.

Node-RED in this stack is **optional dev/demo tooling** for demo orchestration artifacts only.
It is not required for ingestion correctness.

### 4. Verify services

```bash
./scripts/smoke_test.sh
```

Or check individually:

```bash
curl -s http://localhost:8000/health     # API
curl -s http://localhost:8086/health     # InfluxDB
curl -I http://localhost:3000/login      # Grafana
```

### 5. Access the dashboard

Open `http://localhost:8000` in a browser.

### 6. Generate test data

```bash
docker compose -f infra/docker-compose.dev.yml up simulator
```

The simulator publishes telemetry once per second and injects occasional excursion spikes.

---

## 2) Hosted Baseline (DigitalOcean + MongoDB Atlas)

This hosted baseline runs the **core live pipeline** on a Droplet:

- `mosquitto` for MQTT transport
- `worker` for telemetry ingestion and alert/audit generation
- `api` + dashboard UI
- `influxdb` for telemetry storage
- `mongodb` (local) or MongoDB Atlas (via `MONGO_URI`) for audit events

### 1. Provision the Droplet

- Ubuntu 22.04 LTS, minimum 1 vCPU / 1 GB RAM
- Enable firewall: allow ports 22 (SSH), 8000 (API), 80/443 (if nginx is used)
- Add your SSH key

### 2. Install Docker on the Droplet

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 3. Deploy the application

```bash
git clone https://github.com/vlad12-k/oncovax-iot-platform.git
cd oncovax-iot-platform
cp infra/.env.example infra/.env
# Edit infra/.env:
# - Set MONGO_URI to your MongoDB Atlas SRV connection string
# - Set INFLUX_TOKEN, passwords, etc.
```

Start the base stack:

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

**Notes:**
- When `MONGO_URI` points to Atlas, the local `mongodb` container is optional and can be removed or ignored.

### 4. Configure MongoDB Atlas

1. Create a cluster in MongoDB Atlas
2. Create a database user with read/write access to the `oncovax` database
3. Whitelist the Droplet's IP address in Atlas → Network Access
4. Copy the SRV connection string and set it as `MONGO_URI` in your `.env`

### 5. Verify

```bash
curl http://<droplet-ip>:8000/health
curl http://<droplet-ip>:8000/summary
```

---

## 3) Production-Like Deployment (nginx + TLS Scaffold)

For a production-like setup with HTTPS, use `infra/docker-compose.prod.yml` and the included nginx configuration. This stack is **TLS-ready** but not fully hardened for live production.

### 1. Configure your domain

Point your domain's A record to the Droplet's public IP.

### 2. Configure nginx

Edit `infra/nginx/nginx.conf` and replace `your-domain.example.com` with your actual domain.

### 2a. Configure Basic Auth credentials

This production-like stack protects `location /` and acknowledge endpoints with HTTP Basic Auth.
Generate the password file on the host:

```bash
sudo apt install apache2-utils
htpasswd -c ./infra/nginx/.htpasswd oncovax-operator
```

The file is mounted by `infra/docker-compose.prod.yml` at `/etc/nginx/conf.d/.htpasswd`.

### 3. Provision TLS certificates

TLS certificates are **not** automatically provisioned. Options:

**Option A – Let's Encrypt (certbot, recommended for internet-facing deployments):**

```bash
# Install certbot on the host
sudo apt install certbot

# Obtain certificate (standalone mode, port 80 must be open)
sudo certbot certonly --standalone -d your-domain.example.com

# Certificates will be at:
# /etc/letsencrypt/live/your-domain.example.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.example.com/privkey.pem
```

Update `infra/docker-compose.prod.yml` nginx volume mounts to point to these paths.

**Option B – Self-signed (internal / development testing only):**

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout infra/nginx/certs/server.key \
  -out infra/nginx/certs/server.crt
```

### 4. Start the prod-like stack

```bash
docker compose -f infra/docker-compose.prod.yml up -d --build
```

### 5. Verify

```bash
curl -s https://your-domain.example.com/public-health
curl -s -u oncovax-operator:<password> https://your-domain.example.com/summary
```

Production-like topology preserves direct `MQTT -> worker` ingestion authority and does not require Node-RED.

---

## Environment Variables Reference

See `infra/.env.example` for the full list with descriptions.

| Variable | Required | Description |
|---|---|---|
| `MONGO_URI` | Yes | MongoDB connection string (local or Atlas) |
| `MONGO_DB` | Yes | Database name (default: `oncovax`) |
| `MONGO_COLLECTION` | Yes | Collection name (default: `audit_events`) |
| `CORS_ALLOWED_ORIGINS` | Optional | Comma-separated CORS allowlist (default: same-origin only) |
| `INFLUX_URL` | Yes (worker) | InfluxDB base URL |
| `INFLUX_TOKEN` | Yes (worker) | InfluxDB API token |
| `INFLUX_ORG` | Yes (worker) | InfluxDB organisation |
| `INFLUX_BUCKET` | Yes (worker) | InfluxDB bucket |
| `MQTT_HOST` | Yes (worker/sim) | MQTT broker hostname |
| `MQTT_PORT` | Yes (worker/sim) | MQTT broker port |
| `TEMP_THRESHOLD` | Worker | Alert threshold in °C (default: 8.0) |

---

## Demo-Control Contract Deployment Note (Phase B2c)

The Node-RED demo-control artifact (`flows/nodered/demo-control-flow.json`) is scoped to demo topics:

- `oncovax/demo/control/scenario/select`
- `oncovax/demo/control/mode/set`
- `oncovax/demo/control/event/trigger`
- `oncovax/demo/orchestration/status`

Do not rewire canonical telemetry ingestion through Node-RED in this phase.

---

## Restart Policy

Restart behavior differs between the dev/base and production compose files:

- **Local / development (`docker-compose.yml`, `docker-compose.dev.yml`)**
  - Services use `restart: unless-stopped`
  - Containers restart automatically after host reboot
  - Containers do not restart after `docker stop <container>` — they stay stopped until explicitly started again

- **Production (`infra/docker-compose.prod.yml`)**
  - Services use `restart: always`
  - Containers restart automatically after host reboot and after any unexpected exit

In all cases, `docker compose down` stops and removes the containers; they will not restart until you bring the stack up again.

---

## Updating the Deployment

```bash
git pull origin main
# Use the compose file for the mode you are running:
#   docker compose -f infra/docker-compose.yml up -d --build
#   docker compose -f infra/docker-compose.prod.yml up -d --build
```

---

## Rollback

See [RUNBOOK.md](RUNBOOK.md) for rollback procedures.
