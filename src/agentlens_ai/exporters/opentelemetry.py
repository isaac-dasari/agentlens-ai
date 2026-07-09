"""OpenTelemetry-compatible JSONL span export.

This exporter intentionally avoids a hard dependency on an OpenTelemetry collector. It emits a simple
JSONL file that maps AgentLens events into span-like records for downstream ingestion.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_OTEL_EXPORT_PATH = Path(".agentlens/exports/otel-spans.jsonl")


def export_otel_jsonl(
    events: list[dict[str, Any]],
    output: Path = DEFAULT_OTEL_EXPORT_PATH,
) -> Path:
    """Export trace events as OpenTelemetry-style span JSON lines."""

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for index, event in enumerate(events):
            handle.write(json.dumps(_event_to_span(event, index)) + "\n")
    return output


def _event_to_span(event: dict[str, Any], index: int) -> dict[str, Any]:
    run_id = str(event.get("run_id", "run"))
    event_type = str(event.get("event_type", "event"))
    name = str(event.get("name", "unknown"))
    status = "ERROR" if event.get("error") else "OK"

    return {
        "traceId": _stable_hex(run_id, 32),
        "spanId": _stable_hex(f"{run_id}:{index}:{event_type}:{name}", 16),
        "name": f"{event_type}:{name}",
        "kind": "INTERNAL",
        "startTimeUnixNano": _timestamp_to_nanos(str(event.get("timestamp", ""))),
        "durationMs": event.get("duration_ms"),
        "status": {"code": status, "message": event.get("error") or ""},
        "attributes": {
            "agentlens.run_id": run_id,
            "agentlens.event_type": event_type,
            "agentlens.name": name,
        },
    }


def _stable_hex(value: str, length: int) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def _timestamp_to_nanos(value: str) -> int:
    if not value:
        return 0
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return 0
    return int(parsed.timestamp() * 1_000_000_000)
