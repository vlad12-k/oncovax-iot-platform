import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path("/home/runner/work/oncovax-iot-platform/oncovax-iot-platform/services/simulator/runtime_control.py")
spec = importlib.util.spec_from_file_location("runtime_control", MODULE_PATH)
runtime_control = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
sys.modules[spec.name] = runtime_control
spec.loader.exec_module(runtime_control)


RuntimeController = runtime_control.RuntimeController


def test_persistent_scenario_and_profile_update():
    controller = RuntimeController(startup_scenario="normal", startup_profile="standard")
    controller.set_scenario("demo-friendly")
    controller.set_profile("demo")

    snap = controller.snapshot()
    assert snap["scenario"] == "demo-friendly"
    assert snap["profile"] == "demo"


def test_temporary_override_auto_expires_after_duration_cycles():
    controller = RuntimeController(startup_scenario="normal", startup_profile="standard")
    controller.apply_temporary_override("burst_pulse", 2, {"burst_count": 7})

    snap = controller.snapshot()
    assert snap["temporary_override"]["event_type"] == "burst_pulse"
    assert snap["temporary_override"]["remaining_cycles"] == 2

    controller.tick_cycle()
    snap = controller.snapshot()
    assert snap["temporary_override"]["remaining_cycles"] == 1

    controller.tick_cycle()
    snap = controller.snapshot()
    assert snap["temporary_override"] is None


def test_reset_runtime_clears_override_and_restores_startup_defaults():
    controller = RuntimeController(startup_scenario="normal", startup_profile="standard")
    controller.set_scenario("cold-chain breach")
    controller.set_profile("demo")
    controller.apply_temporary_override("offline_pulse", 3, {})

    controller.reset_runtime()
    snap = controller.snapshot()

    assert snap["scenario"] == "normal"
    assert snap["profile"] == "standard"
    assert snap["temporary_override"] is None
