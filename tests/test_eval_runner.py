from pathlib import Path

from agentlens_ai.evals.runner import run_static_eval_file


def test_static_eval_file_passes(tmp_path: Path) -> None:
    eval_file = tmp_path / "evals.yml"
    eval_file.write_text(
        """
tests:
  - name: basic_answer
    output: "The pipeline failed because of schema drift."
    expected_contains:
      - pipeline
      - schema drift
""".strip(),
        encoding="utf-8",
    )

    results = run_static_eval_file(eval_file)

    assert len(results) == 1
    assert results[0].passed is True


def test_static_eval_file_fails_when_text_missing(tmp_path: Path) -> None:
    eval_file = tmp_path / "evals.yml"
    eval_file.write_text(
        """
tests:
  - name: missing_answer
    output: "The answer is unrelated."
    expected_contains:
      - schema drift
""".strip(),
        encoding="utf-8",
    )

    results = run_static_eval_file(eval_file)

    assert len(results) == 1
    assert results[0].passed is False
    assert "schema drift" in results[0].reason
