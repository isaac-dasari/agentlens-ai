"""Decorator-based tracing API."""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from agentlens_ai.privacy import TracePrivacyConfig, sanitize_inputs, sanitize_output
from agentlens_ai.storage.sqlite_store import SQLiteTraceStore
from agentlens_ai.tracing.context import clear_run_id, get_or_create_run_id
from agentlens_ai.tracing.events import EventType, TraceEvent

P = ParamSpec("P")
R = TypeVar("R")


def trace_tool(
    name: str | None = None,
    store: SQLiteTraceStore | None = None,
    privacy: TracePrivacyConfig | None = None,
):
    """Trace a tool function used by an AI agent."""

    trace_store = store or SQLiteTraceStore()
    privacy_config = privacy or TracePrivacyConfig()

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        tool_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            run_id = get_or_create_run_id()
            start = time.perf_counter()

            trace_store.write_event(
                TraceEvent(
                    run_id=run_id,
                    event_type=EventType.TOOL_START,
                    name=tool_name,
                    inputs=sanitize_inputs(args, kwargs, privacy_config),
                )
            )

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                trace_store.write_event(
                    TraceEvent(
                        run_id=run_id,
                        event_type=EventType.TOOL_END,
                        name=tool_name,
                        duration_ms=duration_ms,
                        outputs=sanitize_output(result, privacy_config),
                    )
                )
                return result
            except Exception as exc:
                duration_ms = (time.perf_counter() - start) * 1000
                trace_store.write_event(
                    TraceEvent(
                        run_id=run_id,
                        event_type=EventType.ERROR,
                        name=tool_name,
                        duration_ms=duration_ms,
                        error=repr(exc),
                    )
                )
                raise

        return wrapper

    return decorator


def trace_agent(
    name: str | None = None,
    store: SQLiteTraceStore | None = None,
    privacy: TracePrivacyConfig | None = None,
):
    """Trace an agent entrypoint function."""

    trace_store = store or SQLiteTraceStore()
    privacy_config = privacy or TracePrivacyConfig()

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        agent_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            run_id = get_or_create_run_id()
            start = time.perf_counter()

            trace_store.write_event(
                TraceEvent(
                    run_id=run_id,
                    event_type=EventType.AGENT_START,
                    name=agent_name,
                    inputs=sanitize_inputs(args, kwargs, privacy_config),
                )
            )

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                trace_store.write_event(
                    TraceEvent(
                        run_id=run_id,
                        event_type=EventType.AGENT_END,
                        name=agent_name,
                        duration_ms=duration_ms,
                        outputs=sanitize_output(result, privacy_config),
                    )
                )
                return result
            except Exception as exc:
                duration_ms = (time.perf_counter() - start) * 1000
                trace_store.write_event(
                    TraceEvent(
                        run_id=run_id,
                        event_type=EventType.ERROR,
                        name=agent_name,
                        duration_ms=duration_ms,
                        error=repr(exc),
                    )
                )
                raise
            finally:
                clear_run_id()

        return wrapper

    return decorator
