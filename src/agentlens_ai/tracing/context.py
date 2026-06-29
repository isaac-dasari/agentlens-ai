"""Run context management."""

import contextvars
import uuid

_current_run_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "agentlens_run_id",
    default=None,
)


def get_or_create_run_id() -> str:
    """Return the active run id, creating one if needed."""

    run_id = _current_run_id.get()
    if run_id is None:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        _current_run_id.set(run_id)
    return run_id


def set_run_id(run_id: str) -> None:
    """Set the active run id."""

    _current_run_id.set(run_id)


def clear_run_id() -> None:
    """Clear the active run id."""

    _current_run_id.set(None)
