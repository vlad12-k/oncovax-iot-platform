# Threat Model – OncoVax IoT Monitoring Platform

## Scope

This document describes the current threat model for the OncoVax IoT Monitoring Platform in its MVP and hosted prototype baseline. It is not a formal security audit. It is intended to document known risks, current mitigations, and areas requiring strengthening before any production use.

---

## System Boundaries

```
[Simulator] → MQTT(1883) → [Mosquitto] → [Worker] → [InfluxDB / MongoDB]
                                                           ↑
                                                    [FastAPI :8000]
                                                           ↑
                                              [Browser / Operator Dashboard]
```

External:
- MongoDB Atlas (cloud-managed, TLS enforced by Atlas)
- DigitalOcean Droplet (Linux VM, public IP)

---

## Trust Zones

| Zone | Trust Level | Notes |
|---|---|---|
| Docker internal network | High | Services communicate over Docker bridge network |
| MongoDB Atlas | High | Managed; TLS enforced; network access IP-whitelisted |
| DigitalOcean Droplet | Medium | Requires firewall and hardening |
| Public internet facing API | Low | Currently unauthenticated |
| Operator browser | Low | No session management yet |

---

## Threat Catalogue

### T1 – Unauthenticated API Access

**Description:** The FastAPI service is currently unauthenticated. Any client with network access can read all alerts, read alert details, and POST acknowledgements.

**Impact:** Unauthorised alert acknowledgement; data exfiltration of audit records.

**Current mitigation:** Network-layer restriction (DigitalOcean firewall rules); no public-facing exposure beyond intended operator scope.

**Residual risk:** High. Authentication must be added before broader production use.

**Planned mitigation:** Add API key or session-based authentication.

---

### T2 – MQTT Broker Allows Anonymous Connections

**Description:** Mosquitto is configured with `allow_anonymous true`. Any client that can reach port 1883 can publish arbitrary telemetry messages.

**Impact:** An attacker could inject malicious telemetry, trigger false excursion alerts, or flood the audit collection.

**Current mitigation:** Schema validation in the worker rejects malformed messages. MQTT port not publicly exposed in production.

**Residual risk:** Medium. A crafted but schema-valid message could create false audit records.

**Planned mitigation:** Enable MQTT authentication (username/password or TLS client certificates). Restrict port 1883 to internal Docker network only.

---

### T3 – Sensitive Configuration in Environment Variables

**Description:** InfluxDB tokens, MongoDB URIs, and Grafana credentials are passed via environment variables. If the `.env` file is accidentally committed or if a container is compromised, credentials are exposed.

**Current mitigation:** `.gitignore` excludes `.env` files. `.env.example` contains only placeholder values.

**Residual risk:** Medium. Depends on operator discipline not to commit real values.

**Planned mitigation:** Use a secrets manager (e.g., Docker secrets, HashiCorp Vault, cloud provider secrets) for production.

---

### T4 – Hardcoded Dev Credentials in Compose Files

**Description:** `docker-compose.dev.yml` contains example values for InfluxDB and Grafana admin passwords. If operators do not rotate these, the dev stack may be deployed with weak credentials.

**Current mitigation:** Values are documented as examples and marked for replacement in `.env.example`.

**Residual risk:** Low for dev; High if deployed to internet-facing hosts without rotation.

**Planned mitigation:** Enforce credentials-via-env-file only; remove hardcoded fallbacks from compose files.

---

### T5 – No TLS for Internal API Communication

**Description:** The FastAPI service and MQTT broker communicate without TLS inside the Docker network. If exposed directly to the internet, traffic is unencrypted.

**Current mitigation:** `infra/docker-compose.prod.yml` is designed to put nginx as a reverse proxy in front of the API, handling TLS termination.

**Residual risk:** Medium. TLS must be configured and certificates provisioned before production internet exposure.

**Planned mitigation:** Use nginx + Let's Encrypt (certbot) for TLS termination. See `infra/nginx/nginx.conf`.

---

### T6 – MongoDB Atlas Network Access

**Description:** Atlas allows IP-whitelisting. If the whitelist is too broad (e.g., `0.0.0.0/0`), any client can attempt to connect.

**Current mitigation:** Atlas default configuration requires a connection from an allowlisted IP.

**Residual risk:** Medium. Allowlist must be restricted to Droplet IP only.

**Planned mitigation:** Pin Atlas network access to the Droplet's static IP. Rotate Atlas credentials if IP changes.

---

### T7 – No Rate Limiting on API Endpoints

**Description:** There is no rate limiting on the FastAPI service. A malicious client could flood `/alerts/{id}/acknowledge` or other endpoints.

**Current mitigation:** None at application layer. Network-level restrictions partially mitigate.

**Residual risk:** Low in current deployment scope. Higher as exposure increases.

**Planned mitigation:** Add rate limiting middleware (e.g., `slowapi`) or configure nginx rate limiting.

---

### T8 – Grafana Admin Password

**Description:** Grafana is deployed with a configurable admin password via env. Default in dev compose files is an example value.

**Current mitigation:** Not exposed publicly in dev. Grafana port (3000) should be restricted by firewall in hosted deployments.

**Residual risk:** Low for dev. Medium for hosted instances with open firewall.

**Planned mitigation:** Restrict Grafana port to internal access only in production. Rotate admin credentials.

---

## Summary Risk Table

| ID | Threat | Current Risk | Mitigated by Planned Action |
|---|---|---|---|
| T1 | Unauthenticated API | High | Add API authentication |
| T2 | Anonymous MQTT | Medium | MQTT auth + port restriction |
| T3 | Env var secrets | Medium | Secrets manager |
| T4 | Dev hardcoded creds | Low–High | Env-file-only credentials |
| T5 | No TLS | Medium | nginx + Let's Encrypt |
| T6 | Atlas network access | Medium | IP whitelist restriction |
| T7 | No rate limiting | Low | Rate limiting middleware/nginx |
| T8 | Grafana password | Low–Medium | Firewall + credential rotation |

---

## Out of Scope (Current Baseline)

- Patient data handling (no patient data in this system)
- Code signing or supply chain security
- Full penetration test
- Formal regulatory compliance assessment
