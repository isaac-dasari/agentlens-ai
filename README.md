# AgentLens AI

Local-first reliability testing, observability, and regression checks for AI agents.

AgentLens AI helps developers trace agent runs, inspect tool calls, inject controlled failures, compare reliability across changes, estimate local token/cost impact, and export trace data for downstream observability workflows.

It is designed for engineers building tool-using agents with LangGraph, LangChain, CrewAI, OpenAI tool calling, Bedrock agents, or custom Python frameworks.

## Why AgentLens AI?

AI agents fail across more than one layer. A single answer can depend on prompts, model calls, tool calls, retries, parsing logic, retrieval results, hidden state transitions, and dependency behavior.

AgentLens AI helps answer:

- What did the agent do?
- Which tool calls happened?
- Where did it fail?
- Did a tool timeout, schema drift, or malformed response change behavior?
- Did repeated runs stay reliable?
- Did a code or prompt change increase latency or cost?
- Can this behavior be checked in CI?

## Current MVP

This version includes:

- Python decorators for tracing agents and tools
- Local SQLite trace store
- CLI for initialization, run listing, run timeline, text reporting, and HTML reporting
- Basic trace payload controls with redaction and capture settings
- YAML-based regression eval runner
- YAML-based production-like fault scenarios
- Tool-level fault injection for timeout, rate limit, dependency error, bad JSON, partial response, and schema drift
- Repeated-run stress testing with pass rate, reliability score, p95 latency, cost estimate, and failure attribution
- Baseline-vs-latest stress result comparison
- OpenTelemetry-style JSONL trace export
- Simple tool-agent example
- LangGraph-style graph workflow example
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

## Reliability stress test

Run the same agent under a controlled tool-timeout scenario:

```bash
agentlens stress examples/simple_tool_agent/agent.py \
  --scenario scenarios/tool_timeout.yml \
  --runs 5 \
  --output .agentlens/stress/tool-timeout.json
```

Example output:

```text
AgentLens Stress Result
Scenario: tool_timeout_customer_support
Runs: 5
Passed runs: 0
Pass rate: 0.0
Reliability score: 0.0
Failure attribution: {'timeout': 5, 'tool_timeout': 5}
```

A scenario file looks like this:

```yaml
name: tool_timeout_customer_support
task: "Run the support agent while the document search tool intermittently times out."

faults:
  - target: "search_docs"
    type: "timeout"
    probability: 1.0
    latency_ms: 8000

thresholds:
  pass_rate: 0.0
  max_p95_latency_ms: 12000
```

Supported fault types:

- `timeout`
- `rate_limit`
- `dependency_error`
- `bad_json`
- `partial_response`
- `schema_drift`

## Compare stress results

```bash
agentlens compare .agentlens/stress/baseline.json .agentlens/stress/latest.json
```

The comparison reports pass-rate, reliability-score, latency, and estimated-cost deltas.

## Export traces

```bash
agentlens export-otel --output .agentlens/exports/otel-spans.jsonl
```

This writes OpenTelemetry-style JSONL spans without requiring a collector.

## LangGraph-style demo

```bash
agentlens init
python examples/langgraph_agent/agent.py
agentlens list-runs
agentlens report --html
agentlens eval examples/langgraph_agent/evals.yml
```

This example traces a graph-shaped workflow with route, retrieve, and compose nodes.

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
agentlens eval examples/simple_tool_agent/evals.yml
agentlens stress examples/simple_tool_agent/agent.py --scenario scenarios/tool_timeout.yml
agentlens compare .agentlens/stress/baseline.json .agentlens/stress/latest.json
agentlens export-otel
```

## Who this is for

AgentLens AI is for engineers who build, test, operate, or review AI agents and need local visibility, repeatable reliability checks, and CI-friendly regression signals before introducing a heavier production observability stack.

## What this does not solve

AgentLens AI does not prove that an agent is globally safe or correct. It tests behavior under defined scenarios and makes failure modes visible. The quality of the result depends on scenario design, task oracles, and evaluation policies. It is meant to support engineering review, not replace human judgment.

## Roadmap

- Native OpenAI API wrapper
- LangChain callback integration
- Richer token accounting from provider metadata
- OpenTelemetry collector integration
- GitHub PR regression comment
- Agent run comparison by trace timeline
- Scenario library for common agent failure modes

## Design principles

- Local-first by default
- Simple CLI workflow
- Framework-agnostic core
- Useful without a hosted service
- Built for reliability testing and debugging, not just dashboards
- Clear limitations over inflated claims

## License

MIT
