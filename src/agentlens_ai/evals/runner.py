"""YAML-based regression eval runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class EvalResult:
    name: str
    passed: bool
    reason: str


def _assert_contains(output: str, expected_values: list[str]) -> tuple[bool, str]:
    missing = [value for value in expected_values if value.lower() not in output.lower()]
    if missing:
        return False, f"missing expected text: {', '.join(missing)}"
    return True, "passed"


def run_static_eval_file(path: Path | str) -> list[EvalResult]:
    """Run static eval assertions from a YAML file.

    This MVP supports expected text checks against an explicit output field. Later versions
    will execute agent entrypoints directly and compare baseline/latest traces.
    """

    eval_path = Path(path)
    payload: dict[str, Any] = yaml.safe_load(eval_path.read_text(encoding="utf-8")) or {}
    tests = payload.get("tests", [])

    results: list[EvalResult] = []
    for test in tests:
        name = test.get("name", "unnamed_eval")
        output = str(test.get("output", ""))
        expected_contains = list(test.get("expected_contains", []))

        passed, reason = _assert_contains(output, expected_contains)
        results.append(EvalResult(name=name, passed=passed, reason=reason))

    return results
