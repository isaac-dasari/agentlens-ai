# LangGraph-style AgentLens example

This example shows how to trace a graph-shaped agent workflow with AgentLens.

The default version is dependency-free so it runs in CI. It mirrors a simple LangGraph flow:

1. route the question
2. retrieve context
3. compose an answer

Each node is traced with `trace_tool`, and the workflow entrypoint is traced with `trace_agent`.

## Run

```bash
agentlens init
python examples/langgraph_agent/agent.py
agentlens list-runs
agentlens report --html
agentlens eval examples/langgraph_agent/evals.yml
```

## Why this matters

Graph-based agents are harder to debug than single-call chains. AgentLens makes each node visible in the timeline and HTML report.
