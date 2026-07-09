from agentlens_ai.exporters.opentelemetry import export_otel_jsonl


def test_export_otel_jsonl(tmp_path):
    output = tmp_path / "otel.jsonl"
    export_otel_jsonl(
        [
            {
                "run_id": "run_test",
                "event_type": "tool_start",
                "name": "search_docs",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "duration_ms": None,
                "error": None,
            }
        ],
        output=output,
    )

    content = output.read_text(encoding="utf-8")
    assert "tool_start:search_docs" in content
    assert "agentlens.run_id" in content
