"""Stress runner for production-like agent reliability scenarios."""

from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from agentlens_ai.fault_injection.runtime import SCENARIO_FILE_ENV, SCENARIO_RUN_INDEX_ENV
from agentlens_ai.fault_injection.scenario import load_scenario
from agentlens_ai.reporting.costs import estimate_cost_usd, estimate_event_tokens
from agentlens_ai.storage.sqlite_store import SQLiteTraceStore

DEFAULT_STRESS_RESULT_PATH = Path(".agentlens/stress/latest.json")


def run_stress_test(
    script: Path,
    scenario_path: Path,
    runs: int,
    output: Path = DEFAULT_STRESS_RESULT_PATH,
) -> dict[str, Any]:
    """Run a Python agent script repeatedly under a fault-injection scenario."""

    if runs < 1:
        raise ValueError("runs must be at least 1")

    scenario = load_scenario(scenario_path)
    store = SQLiteTraceStore()
    run_results: list[dict[str, Any]] = []

    for index in range(runs):
        before = set(store.list_runs())
        env = os.environ.copy()
        env[SCENARIO_FILE_ENV] = str(scenario_path)
        env[SCENARIO_RUN_INDEX_ENV] = str(index)

        completed = subprocess.run(  # noqa: S603
            [sys.executable, str(script)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        after = store.list_runs()
        new_run_ids = [run_id for run_id in after if run_id not in before]
        events = _events_for_runs(store, new_run_ids)
        run_results.append(_score_run(index, completed.returncode, new_run_ids, events))

    result = _summarize_stress_results(str(script), str(scenario_path), scenario.name, run_results)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def compare_stress_results(baseline_path: Path, latest_path: Path) -> dict[str, Any]:
    """Compare two stress result JSON files."""

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    latest = json.loads(latest_path.read_text(encoding="utf-8"))

    return {
        "baseline": str(baseline_path),
        "latest": str(latest_path),
        "pass_rate_delta": round(latest["pass_rate"] - baseline["pass_rate"], 4),
        "reliability_score_delta": round(
            latest["reliability_score"] - baseline["reliability_score"],
            4,
        ),
        "p95_latency_ms_delta": round(
            latest["p95_latency_ms"] - baseline["p95_latency_ms"],
            2,
        ),
        "estimated_cost_usd_delta": round(
            latest["estimated_cost_usd"] - baseline["estimated_cost_usd"],
            6,
        ),
        "latest_failure_attribution": latest.get("failure_attribution", {}),
    }


def _events_for_runs(store: SQLiteTraceStore, run_ids: list[str]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for run_id in run_ids:
        events.extend(store.fetch_events(run_id=run_id))
    return events


def _score_run(
    index: int,
    returncode: int,
    run_ids: list[str],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    errors = [event for event in events if event.get("error")]
    faults = [event for event in events if event.get("event_type") == "fault_injected"]
    durations = [event["duration_ms"] for event in events if event.get("duration_ms") is not None]
    tokens = sum(estimate_event_tokens(event) for event in events)
    failure_labels = _failure_labels(errors, faults, returncode)

    return {
        "index": index,
        "run_ids": run_ids,
        "returncode": returncode,
        "passed": returncode == 0 and not errors,
        "event_count": len(events),
        "error_count": len(errors),
        "fault_count": len(faults),
        "failure_labels": failure_labels,
        "latency_ms": round(sum(durations), 2),
        "estimated_tokens": tokens,
        "estimated_cost_usd": estimate_cost_usd(tokens),
    }


def _failure_labels(
    errors: list[dict[str, Any]],
    faults: list[dict[str, Any]],
    returncode: int,
) -> list[str]:
    labels = []
    for fault in faults:
        outputs = fault.get("outputs") or {}
        labels.append(str(outputs.get("fault_type", "fault_injected")))

    for error in errors:
        labels.append(_classify_error(str(error.get("error", ""))))

    if returncode != 0 and not labels:
        labels.append("process_failure")
    return labels


def _classify_error(error: str) -> str:
    lowered = error.lower()
    if "timeout" in lowered:
        return "tool_timeout"
    if "rate_limit" in lowered or "rate limit" in lowered:
        return "rate_limit"
    if "schema" in lowered:
        return "schema_drift"
    if "json" in lowered:
        return "bad_json"
    if "dependency" in lowered:
        return "dependency_error"
    return "runtime_error"


def _summarize_stress_results(
    script: str,
    scenario_path: str,
    scenario_name: str,
    run_results: list[dict[str, Any]],
) -> dict[str, Any]:
    passed = [result for result in run_results if result["passed"]]
    latencies = [float(result["latency_ms"]) for result in run_results]
    failure_counter: Counter[str] = Counter()
    for result in run_results:
        failure_counter.update(result["failure_labels"])

    pass_rate = len(passed) / len(run_results)
    return {
        "script": script,
        "scenario": scenario_name,
        "scenario_path": scenario_path,
        "runs": len(run_results),
        "passed_runs": len(passed),
        "pass_rate": round(pass_rate, 4),
        "reliability_score": round(pass_rate, 4),
        "p95_latency_ms": _p95(latencies),
        "estimated_tokens": sum(result["estimated_tokens"] for result in run_results),
        "estimated_cost_usd": round(
            sum(result["estimated_cost_usd"] for result in run_results),
            6,
        ),
        "failure_attribution": dict(failure_counter),
        "runs_detail": run_results,
    }


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return round(values[0], 2)
    quantiles = statistics.quantiles(values, n=20, method="inclusive")
    return round(quantiles[18], 2)
