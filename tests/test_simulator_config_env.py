import importlib.util
import os
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_MODULE_PATH = REPO_ROOT / "services" / "simulator" / "main.py"
RUNTIME_MODULE_PATH = REPO_ROOT / "services" / "simulator" / "runtime_control.py"


def _load_simulator_main_module():
    runtime_spec = importlib.util.spec_from_file_location("runtime_control", RUNTIME_MODULE_PATH)
    runtime_module = importlib.util.module_from_spec(runtime_spec)
    assert runtime_spec is not None and runtime_spec.loader is not None
    sys.modules[runtime_spec.name] = runtime_module
    runtime_spec.loader.exec_module(runtime_module)

    paho_pkg = types.ModuleType("paho")
    mqtt_pkg = types.ModuleType("paho.mqtt")
    client_pkg = types.ModuleType("paho.mqtt.client")

    class _CallbackAPIVersion:
        VERSION2 = object()

    class _Client:
        def __init__(self, *_args, **_kwargs):
            pass

    client_pkg.CallbackAPIVersion = _CallbackAPIVersion
    client_pkg.Client = _Client
    mqtt_pkg.client = client_pkg
    paho_pkg.mqtt = mqtt_pkg

    sys.modules["paho"] = paho_pkg
    sys.modules["paho.mqtt"] = mqtt_pkg
    sys.modules["paho.mqtt.client"] = client_pkg

    spec = importlib.util.spec_from_file_location("simulator_main", SIM_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_args_reads_simulator_env_defaults(monkeypatch):
    simulator_main = _load_simulator_main_module()
    monkeypatch.setenv("SIM_SCENARIO", "demo-friendly")
    monkeypatch.setenv("SIM_PROFILE", "demo")
    monkeypatch.setenv("SIM_INTERVAL_SECONDS", "0.25")
    monkeypatch.setenv("SIM_SEED", "42")
    monkeypatch.setattr(sys, "argv", ["simulator"])

    args = simulator_main.parse_args()

    assert args.scenario == "demo-friendly"
    assert args.profile == "demo"
    assert args.interval_seconds == 0.25
    assert args.seed == 42


def test_parse_args_treats_empty_env_scenario_as_none(monkeypatch):
    simulator_main = _load_simulator_main_module()
    monkeypatch.setenv("SIM_SCENARIO", "")
    monkeypatch.delenv("SIM_SEED", raising=False)
    monkeypatch.setattr(sys, "argv", ["simulator"])

    args = simulator_main.parse_args()

    assert args.scenario is None
    assert args.seed is None
