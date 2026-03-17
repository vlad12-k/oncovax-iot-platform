# OncoVax IoT Monitoring Platform

Event-driven IoT monitoring platform for regulated biotech environments.

## Overview

This project explores a prototype monitoring platform for biotech and life-science operations where environmental and process conditions must be tracked reliably.  
The current MVP focuses on a cold-storage telemetry pipeline and demonstrates how simulated device data can be published, validated, stored and visualised.

## MVP flow

simulator -> MQTT -> worker -> InfluxDB + MongoDB -> Grafana -> acknowledgement update

## Current stack

- Mosquitto MQTT broker
- Python simulator
- Python worker
- InfluxDB
- MongoDB
- Grafana
- Docker Compose
- GitHub Actions / CodeQL / Dependabot

## What is currently implemented

- telemetry schema for structured message validation
- Python simulator for publishing cold-storage temperature telemetry
- Python worker for validating telemetry and writing to InfluxDB
- threshold-based excursion alert detection
- alert persistence in InfluxDB
- audit-trail baseline in MongoDB
- manual acknowledgement workflow for MongoDB audit records
- Grafana dashboard showing temperature data and excursion spikes
- smoke test script for basic service readiness checks
- documented demo scenarios in `demo/scenarios.md`

## Quickstart

### Start the development stack


## Project structure

- `infra/` - development stack and environment configuration
- `services/simulator/` - telemetry generator
- `services/worker/` - telemetry validation, alerting, and audit write path
- `services/tools/` - operational utility scripts such as alert acknowledgement
- `schemas/` - telemetry message schema
- `docs/` - architecture, runbook, threat model and supporting documentation
- `demo/` - demo scenarios and visual outputs
- `scripts/` - smoke and utility scripts

## Planned next steps

- richer excursion logic
- role-based monitoring views
- stronger integration with wider quality and laboratory workflows
- future API or UI workflow for alert acknowledgement

## Context

This repository supports an IoT case-study and prototype build for a regulated biotech monitoring scenario involving bioreactors, cleanrooms, cold storage and shipments.
