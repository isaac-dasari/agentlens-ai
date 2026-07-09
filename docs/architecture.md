# AgentLens AI Architecture

AgentLens AI is designed as a local-first reliability testing and observability toolkit for tool-using AI agents.

## Architecture

```text
Python agent or tool
        |
        v
trace_agent / trace_tool decorators
        |
        +------------------------------+
        |                              |
        v                              v
TraceEvent model              Fault injection runtime
        |                              |
        v                              v
SQLiteTraceStore              Scenario YAML
        |
        +------------------------------+
        |              |               |
        v              v               v
CLI reports      stress runner     OTEL JSONL export
```

## Core components

### Tracing SDK

The tracing SDK provides decorators that wrap agent entrypoints and tool functions. Each wrapper emits start, end, duration, input, output, fault, and error events.

### Run context

A run id is created when an agent starts and is reused by nested tools. This allows a full agent execution to be reconstructed from individual trace events.

### Fault injection runtime

When the process is launched with a scenario file, traced tools can receive controlled faults such as timeouts, rate limits, dependency errors, malformed JSON, partial responses, or schema drift. Faults are applied by tool name and probability.

### Stress runner

The stress runner executes the same agent script repeatedly under a scenario. It records pass rate, reliability score, p95 latency, estimated tokens, estimated cost, and failure attribution.

### SQLite trace store

The MVP uses SQLite because it is local, zero-config, and easy to inspect. Future storage backends can include Postgres, OpenTelemetry collectors, or hosted observability systems.

### Exporters

The OpenTelemetry-style JSONL exporter maps local trace events into span-like records. This keeps the MVP dependency-light while making downstream observability integration straightforward.

## CLI workflow

```bash
agentlens init
agentlens stress examples/simple_tool_agent/agent.py --scenario scenarios/tool_timeout.yml
agentlens report --html
agentlens export-otel
```

## Reliability model

AgentLens AI treats reliability as observable behavior under repeated runs and controlled failure conditions. The first score is intentionally simple: successful runs divided by total runs. The report also exposes the details needed for engineering review: failure attribution, latency, token estimate, cost estimate, and trace timeline.

## Production hardening path

- Replace local-only storage with pluggable Postgres or ClickHouse backends.
- Export native OpenTelemetry spans to a collector.
- Add provider-backed token usage from model APIs.
- Add trace-level comparison between baseline and candidate runs.
- Add richer task oracles for semantic correctness.
- Add CI comments for pull requests.
- Add scenario packs for common production failure modes.
