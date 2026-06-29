.PHONY: install test lint demo

install:
	pip install -e .[dev]

test:
	pytest

lint:
	ruff check src tests

demo:
	agentlens init
	python examples/simple_tool_agent/agent.py
	agentlens list-runs
	agentlens report
	agentlens eval examples/simple_tool_agent/evals.yml
