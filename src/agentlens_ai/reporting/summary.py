"""Summary reporting for trace events."""

from __future__ import annotations

from collections import Counter
from typing import Any


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a compact summary from trace events."""

    event_counts = Counter(event["event_type"] for event in events)
    run_ids = {event["run_id"] for event in events}
    errors = [event for event in events if event.get("error")]
    durations = [event["duration_ms"] for event in events if event.get("duration_ms") is not None]

    return {
        "runs": len(run_ids),
        "events": len(events),
        "errors": len(errors),
        "agent_runs": event_counts.get("agent_start", 0),
        "tool_calls": event_counts.get("tool_start", 0),
        "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
        "event_counts": dict(event_counts),
    }
