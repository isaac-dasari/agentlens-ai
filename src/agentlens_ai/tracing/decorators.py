"""Decorator-based tracing API."""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from agentlens_ai.storage.sqlite_store import SQLiteTraceStore
from agentlens_ai.tracing.context import clear_run_id, get_or_create_run_id
from agentlens_ai.tracing.events import EventType, TraceEvent

P = ParamSpec("P")
R = TypeVar("R")


def _safe_payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Convert arbitrary function inputs to trace-safe strings."""

    return {
        "args": [repr(arg) for arg in args],
        "kwargs": {key: repr(value) for key, value in kwargs.items()},
    }


def _safe_output(result: Any) -> dict[str, Any]:
    return {"result": repr(result)}


def trace_tool(name: str | None = None, store: SQLiteTraceStore | None = None):
    """Trace a tool function used by an AI agent."""

    trace_store = store or SQLiteTraceStore()

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
                    inputs=_safe_payload(args, kwargs),
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
                        outputs=_safe_output(result),
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


def trace_agent(name: str | None = None, store: SQLiteTraceStore | None = None):
    """Trace an agent entrypoint function."""

    trace_store = store or SQLiteTraceStore()

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
                    inputs=_safe_payload(args, kwargs),
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
                        outputs=_safe_output(result),
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
