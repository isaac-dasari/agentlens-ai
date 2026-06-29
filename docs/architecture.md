# AgentLens AI Architecture

AgentLens AI is designed as a local-first observability and regression-testing toolkit for AI agents.

## MVP architecture

```text
Python agent or tool
        |
        v
trace_agent / trace_tool decorators
        |
        v
TraceEvent model
        |
        v
SQLiteTraceStore
        |
        v
CLI reports and eval checks
```

## Core components

### Tracing SDK

The tracing SDK provides decorators that wrap agent entrypoints and tool functions. Each wrapper emits start, end, duration, input, output, and error events.

### Run context

A run id is created when an agent starts and is reused by nested tools. This allows a full agent execution to be reconstructed from individual trace events.

### SQLite trace store

The MVP uses SQLite because it is local, zero-config, and easy to inspect. Future storage backends can include Postgres, OpenTelemetry exporters, or hosted observability systems.

### CLI

The CLI gives users a fast local workflow:

```bash
agentlens init
agentlens list-runs
agentlens report
agentlens eval examples/simple_tool_agent/evals.yml
```

## Production roadmap

- Token and cost tracking
- Trace comparison across runs
- HTML report
- OpenTelemetry export
- LangGraph integration
- LangChain callback handler
- OpenAI and Bedrock wrappers
- GitHub PR eval comments
