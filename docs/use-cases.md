# AgentLens AI Use Cases

AgentLens AI is useful when an AI agent is doing more than one model call and a print statement is no longer enough.

## Debug a tool using agent

A support agent may call a classifier, a document search tool, and a final answer generator. When the answer is wrong, the developer needs to know which step caused the failure.

AgentLens captures agent and tool events so the developer can inspect the sequence of actions.

## Catch behavior regressions in CI

Agent behavior can change when prompts, tools, retrieval logic, or model parameters change. AgentLens evals let developers define simple expected output checks and run them in CI.

Example command:

agentlens eval examples/simple_tool_agent/evals.yml

## Explain latency and failure patterns

AgentLens records duration for traced functions. This helps identify slow tools, failing tools, and agent runs that need deeper investigation.

## Give teams a local first workflow

Many teams do not want to send early agent traces to a hosted service. AgentLens stores traces locally in SQLite by default, making it useful during prototyping and internal reviews.

## Prepare for production observability

The MVP is intentionally simple, but the roadmap includes OpenTelemetry export, token and cost tracking, HTML reports, run comparison, and framework integrations.

## Ideal users

- AI engineers building tool using agents
- Platform engineers adding AI observability to internal tools
- Data engineers building LLM powered data assistants
- Solutions architects demonstrating production readiness patterns
- Developers who need lightweight regression checks for agent behavior
