from agentlens_ai import trace_agent, trace_tool


@trace_tool(name="lookup_runbook")
def lookup_runbook(issue: str):
    return {
        "runbook": "agent_triage",
        "recommendation": "Review the trace timeline and check slow tool steps.",
    }


@trace_tool(name="estimate_priority")
def estimate_priority(issue: str):
    if "production" in issue.lower():
        return "high"
    return "medium"


@trace_agent(name="tool_agent")
def run_agent(issue: str):
    priority = estimate_priority(issue)
    runbook = lookup_runbook(issue)
    return f"Priority: {priority}. Runbook: {runbook['runbook']}. {runbook['recommendation']}"


if __name__ == "__main__":
    print(run_agent("Production agent latency changed"))
