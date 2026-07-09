# Reliability Model

AgentLens AI measures reliability as repeatable behavior under explicit operating conditions.

## Scope

The reliability score is not a claim of global correctness. It is a scenario-scoped engineering signal. A result means:

```text
Given this agent, this task, this scenario, and this number of repeated runs, this is how often the agent completed without traced errors or process failure.
```

## Primary metrics

| Metric | Meaning |
|---|---|
| Pass rate | Passed runs divided by total runs |
| Reliability score | Initial score equal to pass rate |
| Failure attribution | Count of observed failure labels |
| p95 latency | Approximate high-percentile run latency |
| Estimated tokens | Local estimate from trace payload text |
| Estimated cost | Local estimate from token count |

## Failure attribution

AgentLens AI classifies visible failures into labels such as:

- `tool_timeout`
- `rate_limit`
- `schema_drift`
- `bad_json`
- `dependency_error`
- `runtime_error`
- `process_failure`

These labels are meant to help engineers debug the layer that failed: tool, dependency, schema, runtime, or process execution.

## Why repeated runs matter

Agent behavior can vary across repeated executions even when code does not change. Repeated-run testing makes that instability visible and gives teams a baseline before changing prompts, tools, retrieval, routing, or model configuration.

## Limitations

- The first reliability score is intentionally simple.
- Scenario quality determines signal quality.
- Synthetic faults do not capture every production failure.
- Cost estimates are approximate unless provider usage metadata is added.
- Human review is still needed for safety-sensitive decisions.
