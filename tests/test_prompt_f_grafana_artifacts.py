import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = REPO_ROOT / "grafana" / "dashboards" / "oncovax-observability-final.v1.json"
README_PATH = REPO_ROOT / "grafana" / "README.md"


def test_prompt_f_dashboard_export_exists_and_is_valid_json():
    assert DASHBOARD_PATH.exists()
    parsed = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    assert parsed["title"] == "OncoVax Observability – Prompt F Final"
    assert parsed["uid"] == "oncovax-obsv-f-v1"


def test_prompt_f_dashboard_covers_required_panel_titles():
    parsed = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    titles = {panel["title"] for panel in parsed["panels"]}

    assert "Telemetry ingest (points/min)" in titles
    assert "Active alerts (events/min)" in titles
    assert "Temperature by device" in titles
    assert "Recent active alerts (last 50)" in titles
    assert "Latest metrics by device" in titles
    assert "Signal strength (offline pulse visibility)" in titles
    assert "Alert intensity (value - threshold)" in titles


def test_prompt_f_dashboard_queries_reference_existing_measurements():
    parsed = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    all_queries = "\n".join(
        target.get("query", "")
        for panel in parsed["panels"]
        for target in panel.get("targets", [])
    )

    assert 'r._measurement == "telemetry"' in all_queries
    assert 'r._measurement == "alerts"' in all_queries


def test_prompt_f_grafana_readme_documents_d2_runtime_control_visibility():
    text = README_PATH.read_text(encoding="utf-8")

    assert "oncovax-observability-final.v1.json" in text
    assert "scenario/select" in text
    assert "mode/set" in text
    assert "burst_pulse" in text
    assert "breach_pulse" in text
    assert "offline_pulse" in text
    assert "reset_runtime" in text
