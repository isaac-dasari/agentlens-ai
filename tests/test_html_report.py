from pathlib import Path

from agentlens_ai.reporting.html import generate_html_report


def test_generate_html_report_writes_summary_and_timeline(tmp_path: Path) -> None:
    output_path = tmp_path / "report.html"
    events = [
        {
            "run_id": "run_1",
            "timestamp": "2026-06-29T00:00:00Z",
            "event_type": "agent_start",
            "name": "support_agent",
            "duration_ms": None,
            "error": None,
        },
        {
            "run_id": "run_1",
            "timestamp": "2026-06-29T00:00:01Z",
            "event_type": "tool_end",
            "name": "search_docs",
            "duration_ms": 12.5,
            "error": None,
        },
    ]

    path = generate_html_report(events, output_path)

    assert path == output_path
    html = output_path.read_text(encoding="utf-8")
    assert "AgentLens Report" in html
    assert "support_agent" in html
    assert "search_docs" in html
    assert "12.50 ms" in html
    assert "Event timeline" in html
