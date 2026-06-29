"""Minimal tool-using agent example for AgentLens AI."""

from agentlens_ai import trace_agent, trace_tool


@trace_tool(name="search_docs")
def search_docs(query: str) -> dict[str, object]:
    """Pretend to search an internal knowledge base."""

    return {
        "query": query,
        "results": [
            "Pipeline failures are often caused by schema drift, freshness delays, or broken dependencies."
        ],
    }


@trace_tool(name="classify_issue")
def classify_issue(question: str) -> str:
    """Pretend to classify a support issue."""

    if "pipeline" in question.lower():
        return "data_pipeline"
    return "general"


@trace_agent(name="support_agent")
def run_agent(question: str) -> str:
    issue_type = classify_issue(question)
    docs = search_docs(question)
    first_result = docs["results"][0]
    return f"Issue type: {issue_type}. Answer: {first_result}"


if __name__ == "__main__":
    print(run_agent("Why did my data pipeline fail?"))
