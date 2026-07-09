"""Local token and cost estimates for trace reports.

The estimates are intentionally lightweight. They help developers compare relative cost changes between
runs without depending on a model provider API.
"""

from __future__ import annotations

from typing import Any

DEFAULT_COST_PER_1K_TOKENS = 0.0005


def estimate_tokens(value: Any) -> int:
    """Estimate token count from arbitrary trace payload content."""

    text = _flatten_text(value)
    if not text:
        return 0
    return max(1, round(len(text) / 4))


def estimate_event_tokens(event: dict[str, Any]) -> int:
    """Estimate tokens represented by one trace event."""

    return estimate_tokens(event.get("inputs")) + estimate_tokens(event.get("outputs"))


def estimate_cost_usd(tokens: int, cost_per_1k_tokens: float = DEFAULT_COST_PER_1K_TOKENS) -> float:
    """Estimate cost from token count."""

    return round((tokens / 1000) * cost_per_1k_tokens, 6)


def _flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(f"{key} {_flatten_text(val)}" for key, val in value.items())
    if isinstance(value, list | tuple | set):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)
