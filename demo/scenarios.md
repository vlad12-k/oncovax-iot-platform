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

- Grafana panel query configuration
<img width="1912" height="994" alt="grafana_panel_query" src="https://github.com/user-attachments/assets/52832ef0-7cf3-4d99-b9de-18fc4a37742d" />

- Grafana dashboard view showing cold-storage temperature telemetry
<img width="1909" height="953" alt="grafana_dashboard" src="https://github.com/user-attachments/assets/00441c1b-6c9b-49a7-aa17-4b061201579f" />

- InfluxDB raw telemetry record view
<img width="1909" height="999" alt="influx_raw_data" src="https://github.com/user-attachments/assets/73c841d8-82a3-435d-9a98-2783f9beea25" />

- InfluxDB filtered graph for temperature records
<img width="1901" height="997" alt="influx_temperature_graph" src="https://github.com/user-attachments/assets/6b22bc96-5e1d-4a0e-ba8c-9f118714bdb6" />



## MVP flow

simulator -> MQTT -> worker -> InfluxDB -> Grafana

## Current status

This scenario represents the implemented MVP telemetry baseline.
Future iterations will extend the prototype with richer excursion logic, audit-event storage, and role-based monitoring views.
