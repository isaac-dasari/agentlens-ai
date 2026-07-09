"""Trace event models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types emitted by the AgentLens tracing SDK."""

    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    FAULT_INJECTED = "fault_injected"
    ERROR = "error"


class TraceEvent(BaseModel):
    """Single trace event persisted by AgentLens."""

    run_id: str
    event_type: EventType
    name: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_ms: float | None = None
    inputs: dict[str, Any] | None = None
    outputs: dict[str, Any] | None = None
    error: str | None = None
