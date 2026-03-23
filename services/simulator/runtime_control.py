from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any


SUPPORTED_EVENT_TYPES = {"burst_pulse", "breach_pulse", "offline_pulse", "reset_runtime"}


@dataclass
class TemporaryOverride:
    event_type: str
    duration_cycles: int
    remaining_cycles: int
    params: dict[str, Any] = field(default_factory=dict)


class RuntimeController:
    def __init__(self, startup_scenario: str, startup_profile: str) -> None:
        self.startup_scenario = startup_scenario
        self.startup_profile = startup_profile
        self.persistent_scenario = startup_scenario
        self.persistent_profile = startup_profile
        self.temporary_override: TemporaryOverride | None = None
        self._lock = Lock()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            override = None
            if self.temporary_override is not None:
                override = {
                    "event_type": self.temporary_override.event_type,
                    "duration_cycles": self.temporary_override.duration_cycles,
                    "remaining_cycles": self.temporary_override.remaining_cycles,
                    "params": dict(self.temporary_override.params),
                }
            return {
                "scenario": self.persistent_scenario,
                "profile": self.persistent_profile,
                "temporary_override": override,
                "startup_scenario": self.startup_scenario,
                "startup_profile": self.startup_profile,
            }

    def set_scenario(self, scenario: str) -> None:
        with self._lock:
            self.persistent_scenario = scenario

    def set_profile(self, profile: str) -> None:
        with self._lock:
            self.persistent_profile = profile

    def apply_temporary_override(self, event_type: str, duration_cycles: int, params: dict[str, Any] | None = None) -> None:
        if event_type not in SUPPORTED_EVENT_TYPES or event_type == "reset_runtime":
            raise ValueError(f"Unsupported temporary event_type: {event_type}")
        if duration_cycles <= 0:
            raise ValueError("duration_cycles must be > 0")
        with self._lock:
            self.temporary_override = TemporaryOverride(
                event_type=event_type,
                duration_cycles=duration_cycles,
                remaining_cycles=duration_cycles,
                params=dict(params or {}),
            )

    def reset_runtime(self) -> None:
        with self._lock:
            self.persistent_scenario = self.startup_scenario
            self.persistent_profile = self.startup_profile
            self.temporary_override = None

    def tick_cycle(self) -> None:
        with self._lock:
            if self.temporary_override is None:
                return
            self.temporary_override.remaining_cycles -= 1
            if self.temporary_override.remaining_cycles <= 0:
                self.temporary_override = None
