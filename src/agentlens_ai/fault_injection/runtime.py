"""Runtime fault injection used by traced tools during stress tests."""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from agentlens_ai.fault_injection.scenario import FaultSpec, Scenario, load_scenario

SCENARIO_FILE_ENV = "AGENTLENS_SCENARIO_FILE"
SCENARIO_RUN_INDEX_ENV = "AGENTLENS_SCENARIO_RUN_INDEX"
MAX_SLEEP_MS_ENV = "AGENTLENS_FAULT_MAX_SLEEP_MS"


@dataclass(frozen=True)
class FaultDecision:
    """A concrete injected fault decision for one tool call."""

    target: str
    fault_type: str
    latency_ms: int = 0
    payload: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return {
            "target": self.target,
            "fault_type": self.fault_type,
            "latency_ms": self.latency_ms,
            "payload": self.payload or {},
        }

    def replacement_output(self) -> Any:
        """Return replacement output for non-exception fault types."""

        if self.fault_type == "bad_json":
            return "{malformed_json: true"
        if self.fault_type == "partial_response":
            return {"partial": True, "reason": "injected_partial_response"}
        if self.fault_type == "schema_drift":
            return {
                "schema_version": "injected_drift",
                "unexpected_field": "agentlens_injected_value",
            }
        return None

    @property
    def raises_exception(self) -> bool:
        """Return whether this fault should raise instead of returning replacement output."""

        return self.fault_type in {"timeout", "rate_limit", "dependency_error"}

    def raise_exception(self) -> None:
        """Raise the configured fault exception."""

        if self.fault_type == "timeout":
            raise TimeoutError(f"AgentLensInjectedFault timeout target={self.target}")
        if self.fault_type == "rate_limit":
            raise RuntimeError(f"AgentLensInjectedFault rate_limit target={self.target}")
        if self.fault_type == "dependency_error":
            raise RuntimeError(f"AgentLensInjectedFault dependency_error target={self.target}")


@lru_cache(maxsize=4)
def _load_active_scenario(path: str) -> Scenario:
    return load_scenario(Path(path))


def get_active_scenario() -> Scenario | None:
    """Return the active scenario, if the process is running under a stress test."""

    scenario_file = os.environ.get(SCENARIO_FILE_ENV)
    if not scenario_file:
        return None
    return _load_active_scenario(scenario_file)


def maybe_inject_fault(tool_name: str) -> FaultDecision | None:
    """Return a fault decision for a tool call, or None when no fault applies."""

    scenario = get_active_scenario()
    if scenario is None:
        return None

    run_index = os.environ.get(SCENARIO_RUN_INDEX_ENV, "0")
    for fault in scenario.matching_faults(tool_name):
        if _should_apply(scenario, fault, tool_name, run_index):
            _bounded_sleep(fault.latency_ms)
            return FaultDecision(
                target=tool_name,
                fault_type=fault.type,
                latency_ms=fault.latency_ms,
                payload=fault.payload,
            )
    return None


def _should_apply(scenario: Scenario, fault: FaultSpec, tool_name: str, run_index: str) -> bool:
    probability = max(0.0, min(1.0, fault.probability))
    if probability >= 1.0:
        return True
    seed = f"{scenario.name}:{run_index}:{tool_name}:{fault.type}:{fault.target}"
    return random.Random(seed).random() < probability


def _bounded_sleep(latency_ms: int) -> None:
    if latency_ms <= 0:
        return
    max_sleep_ms = int(os.environ.get(MAX_SLEEP_MS_ENV, "100"))
    sleep_ms = min(latency_ms, max_sleep_ms)
    time.sleep(sleep_ms / 1000)
