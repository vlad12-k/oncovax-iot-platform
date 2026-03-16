# MVP Demo Scenarios

## Scenario 1: Cold-storage telemetry pipeline

This scenario demonstrates the baseline OncoVax MVP monitoring flow for a cold-storage asset.

A Python simulator publishes temperature telemetry for the asset type `coldstorage` to the MQTT topic `oncovax/telemetry`.
A Python worker subscribes to the topic, validates incoming messages against the telemetry schema, and writes valid records to InfluxDB.
Grafana then visualises the stored telemetry as a time-series dashboard.

The simulated data stream includes normal cold-storage temperature values around 4°C, with injected excursion spikes at 10.5°C.
These excursion spikes are visible in the Grafana dashboard and can also be verified in the InfluxDB Data Explorer.

## Components used

- Mosquitto MQTT broker
- Python simulator
- Python worker
- InfluxDB
- Grafana

## Evidence collected

The following evidence was captured during the prototype demonstration:

- Grafana dashboard view showing cold-storage temperature telemetry
- Grafana panel query configuration
- InfluxDB filtered graph for temperature records
- InfluxDB raw telemetry record view

## MVP flow

simulator -> MQTT -> worker -> InfluxDB -> Grafana

## Current status

This scenario represents the implemented MVP telemetry baseline.
Future iterations will extend the prototype with richer excursion logic, audit-event storage, and role-based monitoring views.
