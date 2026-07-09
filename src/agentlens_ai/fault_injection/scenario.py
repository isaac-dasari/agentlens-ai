"""Scenario file parsing for production-like agent fault tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class FaultSpec:
    """A single controlled fault that can be injected into a traced tool."""

    target: str
    type: str
    probability: float = 1.0
    latency_ms: int = 0
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Scenario:
    """A reliability scenario loaded from YAML."""

    name: str
    task: str = ""
    faults: tuple[FaultSpec, ...] = ()
    expected: dict[str, Any] = field(default_factory=dict)
    thresholds: dict[str, Any] = field(default_factory=dict)

    def matching_faults(self, tool_name: str) -> list[FaultSpec]:
        """Return faults that target a tool name."""

        return [fault for fault in self.faults if fault.target in {tool_name, "*"}]


def load_scenario(path: Path | str) -> Scenario:
    """Load a scenario YAML file."""

    scenario_path = Path(path)
    payload = yaml.safe_load(scenario_path.read_text(encoding="utf-8")) or {}
    faults = []

    for raw_fault in payload.get("faults", []):
        faults.append(
            FaultSpec(
                target=str(raw_fault["target"]),
                type=str(raw_fault["type"]),
                probability=float(raw_fault.get("probability", 1.0)),
                latency_ms=int(raw_fault.get("latency_ms", 0)),
                payload=dict(raw_fault.get("payload", {})),
            )
        )

    return Scenario(
        name=str(payload.get("name", scenario_path.stem)),
        task=str(payload.get("task", "")),
        faults=tuple(faults),
        expected=dict(payload.get("expected", {})),
        thresholds=dict(payload.get("thresholds", {})),
    )
