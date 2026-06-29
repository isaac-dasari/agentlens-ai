from agentlens_ai.reporting.summary import summarize_events


def test_summarize_events_counts_runs_and_errors() -> None:
    events = [
        {"run_id": "run_1", "event_type": "agent_start", "duration_ms": None},
        {"run_id": "run_1", "event_type": "tool_start", "duration_ms": None},
        {"run_id": "run_1", "event_type": "tool_end", "duration_ms": 10.0},
        {"run_id": "run_1", "event_type": "error", "duration_ms": 2.0, "error": "boom"},
    ]

    summary = summarize_events(events)

    assert summary["runs"] == 1
    assert summary["events"] == 4
    assert summary["errors"] == 1
    assert summary["tool_calls"] == 1
    assert summary["avg_duration_ms"] == 6.0
