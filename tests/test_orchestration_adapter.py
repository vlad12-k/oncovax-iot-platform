import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path("/home/runner/work/oncovax-iot-platform/oncovax-iot-platform/services/orchestration_adapter/main.py")
spec = importlib.util.spec_from_file_location("orchestration_adapter_main", MODULE_PATH)
adapter = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
sys.modules[spec.name] = adapter
spec.loader.exec_module(adapter)


def test_validate_scenario_select_maps_to_internal_runtime_command():
    status, mapped = adapter.validate_and_map(
        adapter.CONTROL_TOPICS["scenario/select"],
        {
            "command_id": "cmd-1",
            "issued_at": "2026-03-23T20:00:00Z",
            "scenario": "demo-friendly",
        },
    )

    assert status["status"] == "accepted"
    assert mapped == {
        "action": "set_scenario",
        "command_id": "cmd-1",
        "issued_at": "2026-03-23T20:00:00Z",
        "scenario": "demo-friendly",
    }


def test_validate_mode_set_rejects_non_boolean_enabled():
    status, mapped = adapter.validate_and_map(
        adapter.CONTROL_TOPICS["mode/set"],
        {
            "command_id": "cmd-2",
            "issued_at": "2026-03-23T20:00:00Z",
            "enabled": "yes",
        },
    )

    assert status["status"] == "rejected"
    assert "enabled must be boolean" in status["reason"]
    assert mapped is None


def test_validate_event_trigger_allows_only_locked_event_types():
    status, mapped = adapter.validate_and_map(
        adapter.CONTROL_TOPICS["event/trigger"],
        {
            "command_id": "cmd-3",
            "issued_at": "2026-03-23T20:00:00Z",
            "event_type": "unknown_event",
        },
    )

    assert status["status"] == "rejected"
    assert "event_type must be one of" in status["reason"]
    assert mapped is None


def test_validate_event_trigger_reset_runtime_maps_without_duration():
    status, mapped = adapter.validate_and_map(
        adapter.CONTROL_TOPICS["event/trigger"],
        {
            "command_id": "cmd-4",
            "issued_at": "2026-03-23T20:00:00Z",
            "event_type": "reset_runtime",
        },
    )

    assert status["status"] == "accepted"
    assert mapped == {
        "action": "reset_runtime",
        "command_id": "cmd-4",
        "issued_at": "2026-03-23T20:00:00Z",
        "event_type": "reset_runtime",
    }
