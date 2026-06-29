# Demo Output

This page shows what a new user should expect after running the local demo.

## Commands

```bash
agentlens init
python examples/simple_tool_agent/agent.py
agentlens list-runs
agentlens report
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
3. Show a local report
4. Run regression checks
5. Fail CI when an eval fails
