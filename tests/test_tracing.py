from pathlib import Path

from agentlens_ai.storage.sqlite_store import SQLiteTraceStore
from agentlens_ai.tracing.decorators import trace_agent, trace_tool


def test_trace_agent_and_tool_write_events(tmp_path: Path) -> None:
    store = SQLiteTraceStore(tmp_path / "traces.db")

    @trace_tool(name="lookup", store=store)
    def lookup(value: str) -> str:
        return f"found {value}"

    @trace_agent(name="agent", store=store)
    def agent(question: str) -> str:
        return lookup(question)

    assert agent("pipeline") == "found pipeline"

    events = store.fetch_events()
    event_types = [event["event_type"] for event in events]

    assert "agent_start" in event_types
    assert "agent_end" in event_types
    assert "tool_start" in event_types
    assert "tool_end" in event_types
    assert len(store.list_runs()) == 1
