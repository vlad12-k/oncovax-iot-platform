# OncoVax IoT Monitoring Platform

Event-driven IoT monitoring platform for regulated biotech environments.

## Overview

This project explores a prototype monitoring platform for biotech and life-science operations where environmental and process conditions must be tracked reliably.  
The current MVP focuses on a cold-storage telemetry pipeline and demonstrates how simulated device data can be published, validated, stored and visualised.

## MVP flow

simulator -> MQTT -> worker -> InfluxDB + MongoDB -> Grafana -> acknowledgement update

## The platform has also been extended with:

FastAPI service -> alert retrieval, summary, and acknowledgement support
FastAPI-served dashboard -> lightweight operational UI
MongoDB Atlas -> hosted audit data baseline
DigitalOcean -> hosted application baseline

## Current stack

- Mosquitto MQTT broker
- Python simulator
- Python worker
- InfluxDB
- MongoDB
- MongoDB Atlas
- Grafana
- FastAPI
- lightweight HTML/CSS/JavaScript operational dashboard
- Docker Compose
- DigitalOcean Droplet
- GitHub Actions / CodeQL / Dependabot

## What is currently implemented

The project currently includes the following delivered capabilities:

- telemetry schema for structured message validation
- Python simulator for publishing cold-storage temperature telemetry
- Python worker for validating telemetry and writing to InfluxDB
- threshold-based excursion alert detection
- alert persistence in InfluxDB
- audit-trail baseline in MongoDB
- manual acknowledgement workflow for MongoDB audit records
- Node-RED telemetry flow baseline
- FastAPI service for:
  	`/health`
  	`/alerts`
  	`/alerts/{alert_id}`
  	`/summary`
- acknowledgement updates
-	containerized API baseline
- deployment-readiness baseline with configuration and health checks
- lightweight operational dashboard served by FastAPI
- MongoDB Atlas integration baseline for hosted audit data
- DigitalOcean hosted application baseline
-	smoke test script for service readiness checks
- documented demo scenarios in `demo/scenarios.md`


### MVP progression

The project was developed through a sequence of practical increments:

  1.	cold-storage telemetry pipeline baseline
  2.	excursion alert detection and persistence
  3.	audit-trail baseline for excursion alerts
  4.	manual acknowledgement workflow baseline
  5.	project polish and smoke-test baseline
  6.	Node-RED flow baseline
  7.	API baseline for alert retrieval and acknowledgement
  8.	containerized API baseline
  9.	deployment-readiness baseline
  10.	API service maturity baseline
  11.	lightweight operational UI baseline
  12.	MongoDB Atlas integration baseline
  13.	DigitalOcean hosted application baseline

Full scenario evidence and screenshots are documented in: 
`demo/scenarios.md`



## Project structure

- `infra/` - development stack and environment configuration
- `services/simulator/` - telemetry generator
- `services/worker/` - telemetry validation, alerting, and audit write path
- `services/api/` - FastAPI service and hosted dashboard delivery
- `services/tools/` - operational utility scripts such as alert acknowledgement
- `services/web/` - lightweight operational dashboard assets
- `schemas/` - telemetry message schema
- `docs/` - architecture, runbook, threat model and supporting documentation
- `demo/` - demo scenarios and visual outputs
- `scripts/` - smoke and utility scripts
- `tests/` - supporting test assets

## Local development quickstart

### Start the local development stack
`docker compose -f infra/docker-compose.dev.yml up -d --build`

### Verify service readiness
`./scripts/smoke_test.sh`

### Check API health
`curl -s http://localhost:8000/health`

### Check alert summary
`curl -s http://localhost:8000/summary | python -m json.tool`

### Hosted baseline
The project now also includes a hosted baseline where:
-	audit data is stored in MongoDB Atlas
-	the application baseline is hosted on a DigitalOcean Droplet
-	the FastAPI service and lightweight operational dashboard are available outside the local development environment

This hosted baseline does not yet represent a full production deployment of the entire stack, but it demonstrates a practical cloud-hosted application path beyond local and Codespaces-only execution.

### Operational interface

The lightweight dashboard provides:

-	alert summary cards
-	alert table for operational review
-	filtering by acknowledgement state
-	client-side search over alert records

This creates a simple presentation layer over the FastAPI service and MongoDB-backed alert data.

### Data layers
The platform currently separates responsibilities across storage layers:

## InfluxDB

Used for:
- telemetry storage
- time-series alert visibility
- Grafana-backed trend and excursion visualisation
  
### MongoDB / MongoDB Atlas

Used for:
- audit-trail records
- acknowledgement state
- operational alert history
- API-backed alert retrieval and workflow support
  
## Grafana role

Grafana remains the time-series visualisation layer for telemetry and excursion-style monitoring views.
If no fresh telemetry is present in the selected time window, Grafana panels may show No data, which reflects the available dataset rather than a failure of the overall architecture.

## Security and quality baseline

The repository includes basic quality and governance measures such as:
- GitHub Actions
- CodeQL
- Dependabot
- structured schema validation
- documented runbook and threat-model support

### Current limitations

This is still an MVP-oriented prototype rather than a full production platform.
Current limitations include:
- simplified telemetry generation
- limited data volume in demo scenarios
- basic acknowledgement workflow
- lightweight UI rather than full operational web application
- partial cloud-hosted baseline rather than full hosted stack migration
- no full authentication / role model yet
- no advanced production observability or retention strategy yet

## Planned next steps

Planned future improvements include:
- richer excursion logic
- stronger role-based operational workflows
- expanded alert lifecycle management
- fuller hosted deployment architecture
- stronger integration with wider quality and laboratory workflows
- improved production-style data volume and monitoring coverage

## Why this project matters

This project demonstrates practical experience across:
- IoT-style telemetry ingestion
- event-driven processing
- time-series and document-database separation
- API design
- operational dashboard delivery
- Docker-based local orchestration
- managed cloud database integration
- hosted application deployment baseline

It is intended as both a technical case study and a portfolio-grade prototype for regulated monitoring scenarios.


## Demo evidence
Scenario write-ups and screenshots are available in:
`demo/scenarios.md`
