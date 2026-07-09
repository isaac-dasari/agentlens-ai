# Scenario Format

AgentLens AI scenarios are YAML files that describe production-like failures to inject into traced tools.

## Example

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

## Fields

| Field | Required | Description |
|---|---:|---|
| `name` | yes | Stable scenario name |
| `task` | no | Human-readable task description |
| `faults` | yes | List of tool faults to inject |
| `expected` | no | Notes about expected behavior |
| `thresholds` | no | Desired reliability, latency, or policy thresholds |

## Fault fields

| Field | Required | Description |
|---|---:|---|
| `target` | yes | Traced tool name or `*` for all tools |
| `type` | yes | Fault type |
| `probability` | no | 0.0 to 1.0 probability per run/tool |
| `latency_ms` | no | Simulated latency hint for timeout-style faults |
| `payload` | no | Optional scenario-specific metadata |

## Supported fault types

- `timeout`
- `rate_limit`
- `dependency_error`
- `bad_json`
- `partial_response`
- `schema_drift`

## Design note

Faults are deterministic for a scenario, run index, tool name, target, and fault type. This makes stress runs easier to reproduce while still allowing probability-based scenarios.
