# Demo Output

This page shows what a new user should expect after running the local demo.

## Commands

```bash
agentlens init
python examples/simple_tool_agent/agent.py
agentlens list-runs
agentlens report
agentlens report --html
agentlens eval examples/simple_tool_agent/evals.yml
```

## Agent output

```text
Issue type: data_pipeline. Answer: Pipeline failures are often caused by schema drift, freshness delays, or broken dependencies.
```

## Report output

```text
AgentLens Report
Total runs: 1
Total events: 6
Errors: 0
Tool calls: 2
Agent runs: 1
Avg recorded duration: 1.0 ms
```

## Run timeline output

After copying a run id from `agentlens list-runs`:

```bash
agentlens show run_example
```

The command prints an ordered timeline with timestamp, event type, function name, duration, and status.

## HTML report output

```text
HTML report written to .agentlens/reports/latest.html
```

The generated HTML report includes summary cards and an event timeline with run id, timestamp, event type, function name, duration, and status.

## Eval output

```text
AgentLens Eval Results
pipeline_failure_answer_mentions_schema_drift PASS passed
answer_mentions_dependencies PASS passed
```

## What this proves

The MVP proves the basic loop:

1. Trace an agent run
2. Persist events locally
3. Show a local text report
4. Inspect one run timeline
5. Generate a local HTML report
6. Run regression checks
7. Fail CI when an eval fails
