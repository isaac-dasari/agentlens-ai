# AgentLens AI

Lightweight observability and regression testing for AI agents.

AgentLens AI helps developers trace agent runs, tool calls, latency, errors, and behavior changes using a local-first workflow. It is designed for engineers building agents with LangGraph, LangChain, CrewAI, OpenAI tool calling, Bedrock agents, or custom Python frameworks.

## Why AgentLens AI?

AI agents fail in ways normal logs do not explain. A single answer may depend on prompts, model calls, tool calls, retries, parsing logic, retrieval results, and hidden state transitions.

AgentLens AI helps answer:

- What did the agent do?
- Which tool calls happened?
- Where did it fail?
- How long did each step take?
- Did a code or prompt change break behavior?
- Can this behavior be checked in CI?

## Current MVP

This first version includes:

- Python decorators for tracing agents and tools
- Local SQLite trace store
- CLI for initialization, run listing, run timeline, text reporting, and HTML reporting
- Basic trace payload controls with redaction and capture settings
- YAML-based regression eval runner
- Example tool-using agents
- Pytest test suite
- GitHub Actions CI

## Install locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 60-second demo

```bash
agentlens init
python examples/simple_tool_agent/agent.py
agentlens list-runs
agentlens report
agentlens report --html
agentlens eval examples/simple_tool_agent/evals.yml
```

The HTML report is written to:

```text
.agentlens/reports/latest.html
```

## Python SDK

```python
from agentlens_ai import trace_agent, trace_tool

@trace_tool(name="search_docs")
def search_docs(query: str):
    return {"results": ["Schema drift can break downstream pipelines."]}

@trace_agent(name="support_agent")
def run_agent(question: str):
    docs = search_docs(question)
    return f"Answer based on: {docs['results'][0]}"

run_agent("Why did my data pipeline fail?")
```

## Payload controls

```python
from agentlens_ai import TracePrivacyConfig, trace_agent

privacy = TracePrivacyConfig(capture_inputs=False, capture_outputs=False)

@trace_agent(name="support_agent", privacy=privacy)
def run_agent(question: str):
    return "answer"
```

By default, AgentLens redacts common private keys, truncates long values, and stores traces locally.

## CLI

```bash
agentlens init
agentlens list-runs
agentlens show <run_id>
agentlens report
agentlens report --html
agentlens report --html --output .agentlens/reports/demo.html
agentlens eval examples/simple_tool_agent/evals.yml
```

## Example report

```text
AgentLens Report
Total runs: 1
Total events: 6
Errors: 0
Tool calls: 2
Agent runs: 1
Avg recorded duration: 1.0 ms
HTML report written to .agentlens/reports/latest.html
```

## What the HTML report shows

- Run count
- Event count
- Error count
- Tool call count
- Average recorded duration
- Ordered event timeline with run id, timestamp, event type, name, duration, and status

## Who this is for

AgentLens AI is for engineers who build, test, operate, or review AI agents and need lightweight local visibility before introducing a heavier production observability stack.

## Roadmap

- OpenAI API wrapper
- LangChain callback integration
- LangGraph example
- Cost and token tracking
- Trace export to OpenTelemetry
- GitHub PR regression comment
- Agent run comparison

## Design principles

- Local-first by default
- Simple CLI workflow
- Framework-agnostic core
- Useful without a hosted service
- Built for debugging and regression testing, not just dashboards

## License

MIT
