# MVP Demo Scenarios

## Scenario 1: Cold-storage telemetry pipeline

This scenario demonstrates the baseline OncoVax MVP monitoring flow for a cold-storage asset.

A Python simulator publishes temperature telemetry for the asset type `coldstorage` to the MQTT topic `oncovax/telemetry`.
A Python worker subscribes to the topic, validates incoming messages against the telemetry schema, and writes valid records to InfluxDB.
Grafana then visualises the stored telemetry as a time-series dashboard.

The simulated data stream includes normal cold-storage temperature values around 4°C, with injected excursion spikes at 10.5°C.
These excursion spikes are visible in the Grafana dashboard and can also be verified in the InfluxDB Data Explorer.

## Stack used

- Mosquitto MQTT broker
- Python simulator
- Python worker
- InfluxDB
- Grafana

## What this MVP demonstrates

- structured telemetry publication through MQTT
- schema-aware processing in a dedicated Python worker
- time-series persistence in InfluxDB
- dashboard visualisation in Grafana
- visible abnormal temperature spikes for excursion-style scenarios

## Demo outputs

### Grafana panel query configuration
![Grafana panel query](https://github.com/user-attachments/assets/52832ef0-7cf3-4d99-b9de-18fc4a37742d)

### Grafana dashboard view showing cold-storage telemetry
![Grafana dashboard](https://github.com/user-attachments/assets/00441c1b-6c9b-49a7-aa17-4b061201579f)

### InfluxDB raw telemetry record view
![InfluxDB raw data](https://github.com/user-attachments/assets/73c841d8-82a3-435d-9a98-2783f9beea25)

### InfluxDB filtered graph for temperature records
![InfluxDB temperature graph](https://github.com/user-attachments/assets/6b22bc96-5e1d-4a0e-ba8c-9f118714bdb6)

## MVP flow

simulator -> MQTT -> worker -> InfluxDB -> Grafana

## Current status

This scenario represents the implemented MVP telemetry baseline.
Planned next steps include richer excursion logic, audit-event storage, and role-based monitoring views.

---

## Scenario 2: Excursion alert detection and persistence

This scenario demonstrates the second MVP increment for the OncoVax monitoring platform.  
In this iteration, the worker no longer acts only as a validation and persistence component. It also applies a threshold-based excursion rule to incoming cold-storage telemetry.

When a temperature reading exceeds the configured threshold, the worker generates an alert event and writes that event into a dedicated `alerts` measurement in InfluxDB. This extends the platform from a monitoring-only pipeline into an event-aware monitoring workflow.

In the current implementation, the excursion rule is based on the `temperature` metric and a configurable threshold value. During validation, injected temperature spikes at `10.5°C` triggered alert creation, which was then confirmed in both InfluxDB and Grafana.

## What this increment adds

- threshold-based excursion detection in the Python worker
- alert event generation when cold-storage temperature exceeds the configured rule
- alert persistence in the `alerts` measurement in InfluxDB
- alert visibility in both InfluxDB Data Explorer and Grafana

## Sprint 2 outputs

### InfluxDB alerts graph
<img width="1884" height="983" alt="1 influxdb_alerts_graph" src="https://github.com/user-attachments/assets/d2e16d22-9ee5-4fff-a45f-6b252cf76eb7" />


### InfluxDB alerts raw data
<img width="1911" height="990" alt="1 fig_influxdb_alerts_raw_data" src="https://github.com/user-attachments/assets/64264a5c-2248-4c1f-8470-b4033d310b22" />

### Grafana excursion alert values
<img width="1907" height="966" alt="fig_grafana_excursion_alert_values" src="https://github.com/user-attachments/assets/d7f668ba-9318-4efc-b6af-f286c429aa66" />





## Updated MVP flow

simulator -> MQTT -> worker -> InfluxDB -> Grafana + alert event generation

## Sprint 2 status

This increment confirms that the platform can not only ingest and visualise telemetry, but also detect threshold breaches and persist alert events for future audit-trail and acknowledgement workflows.
