from pathlib import Path

from agentlens_ai.stress.runner import compare_stress_results, run_stress_test


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stress_runner_records_faults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result_path = tmp_path / "stress.json"
    result = run_stress_test(
        script=REPO_ROOT / "examples/simple_tool_agent/agent.py",
        scenario_path=REPO_ROOT / "scenarios/tool_timeout.yml",
        runs=1,
        output=result_path,
    )

    assert result_path.exists()
    assert result["runs"] == 1
    assert result["passed_runs"] == 0
    assert result["failure_attribution"]["timeout"] == 1
    assert result["failure_attribution"]["tool_timeout"] >= 1


def test_compare_stress_results(tmp_path):
    baseline = tmp_path / "baseline.json"
    latest = tmp_path / "latest.json"
    baseline.write_text(
        '{"pass_rate": 1.0, "reliability_score": 1.0, '
        '"p95_latency_ms": 10.0, "estimated_cost_usd": 0.01}',
        encoding="utf-8",
    )
    latest.write_text(
        '{"pass_rate": 0.5, "reliability_score": 0.5, '
        '"p95_latency_ms": 20.0, "estimated_cost_usd": 0.02, '
        '"failure_attribution": {"tool_timeout": 1}}',
        encoding="utf-8",
    )

    result = compare_stress_results(baseline, latest)

    assert result["pass_rate_delta"] == -0.5
    assert result["p95_latency_ms_delta"] == 10.0
    assert result["latest_failure_attribution"] == {"tool_timeout": 1}
