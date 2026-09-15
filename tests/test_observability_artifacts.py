import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = REPO_ROOT / "grafana" / "dashboards" / "oncovax-observability-final.v1.json"
README_PATH = REPO_ROOT / "grafana" / "README.md"


def test_dashboard_export_exists_and_is_valid_json():
    assert DASHBOARD_PATH.exists()
    parsed = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    assert parsed["title"] == "OncoVax Observability"
    assert parsed["uid"] == "oncovax-obsv-f-v1"


def test_dashboard_covers_required_panel_titles():
    parsed = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    titles = {panel["title"] for panel in parsed["panels"]}

    assert "Telemetry ingest (points/min)" in titles
    assert "Active alerts (events/min)" in titles
    assert "Temperature by device" in titles
    assert "Recent active alerts (last 50)" in titles
    assert "Latest metrics by device" in titles
    assert "Signal strength (offline pulse visibility)" in titles
    assert "Alert intensity (value - threshold)" in titles


def test_dashboard_queries_reference_existing_measurements():
    parsed = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    all_queries = "\n".join(
        target.get("query", "")
        for panel in parsed["panels"]
        for target in panel.get("targets", [])
    )

    assert 'r._measurement == "telemetry"' in all_queries
    assert 'r._measurement == "alerts"' in all_queries


def test_local_dashboard_and_datasource_are_provisioned():
    import yaml
    services = yaml.safe_load((REPO_ROOT / 'infra/docker-compose.dev.yml').read_text())['services']
    volumes = services['grafana']['volumes']
    assert '../grafana/dashboards:/var/lib/grafana/dashboards:ro' in volumes
    assert '../grafana/provisioning/datasources:/etc/grafana/provisioning/datasources:ro' in volumes
    datasource = yaml.safe_load((REPO_ROOT / 'grafana/provisioning/datasources/influxdb.yml').read_text())
    assert datasource['datasources'][0]['url'] == 'http://influxdb:8086'


def test_dev_compose_worker_configures_simulator_compat_topic():
    compose_text = (REPO_ROOT / "infra" / "docker-compose.dev.yml").read_text(encoding="utf-8")
    assert "worker:" in compose_text
    worker_block = compose_text.split("worker:", 1)[1].split("orchestration-adapter:", 1)[0]
    assert "MQTT_SIMULATOR_COMPAT_TOPIC=oncovax/telemetry/simulator" in worker_block
