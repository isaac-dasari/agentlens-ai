"""Privacy controls for AgentLens trace payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEFAULT_REDACT_KEYS = {
    "api_key",
    "authorization",
    "auth",
    "bearer",
    "cookie",
    "email",
    "key",
    "password",
    "secret",
    "token",
}

REDACTED = "[REDACTED]"


@dataclass(frozen=True)
class TracePrivacyConfig:
    """Controls what AgentLens stores in local traces."""

    capture_inputs: bool = True
    capture_outputs: bool = True
    redact_keys: set[str] = field(default_factory=lambda: set(DEFAULT_REDACT_KEYS))
    max_repr_length: int = 500


def _is_sensitive_key(key: str, config: TracePrivacyConfig) -> bool:
    normalized = key.lower()
    return any(token in normalized for token in config.redact_keys)


def _truncate(value: str, config: TracePrivacyConfig) -> str:
    if len(value) <= config.max_repr_length:
        return value
    return value[: config.max_repr_length] + "..."


def sanitize_value(value: Any, config: TracePrivacyConfig | None = None) -> Any:
    """Return a trace-safe representation of a value."""

    config = config or TracePrivacyConfig()

    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _is_sensitive_key(key_text, config):
                sanitized[key_text] = REDACTED
            else:
                sanitized[key_text] = sanitize_value(item, config)
        return sanitized

    if isinstance(value, (list, tuple, set)):
        return [sanitize_value(item, config) for item in value]

    return _truncate(repr(value), config)


def sanitize_inputs(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    config: TracePrivacyConfig | None = None,
) -> dict[str, Any] | None:
    """Sanitize function arguments for tracing."""

    config = config or TracePrivacyConfig()
    if not config.capture_inputs:
        return None

    return {
        "args": [sanitize_value(arg, config) for arg in args],
        "kwargs": sanitize_value(kwargs, config),
    }


def sanitize_output(value: Any, config: TracePrivacyConfig | None = None) -> dict[str, Any] | None:
    """Sanitize function output for tracing."""

    config = config or TracePrivacyConfig()
    if not config.capture_outputs:
        return None

    return {"result": sanitize_value(value, config)}
