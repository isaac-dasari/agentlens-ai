"""LangGraph-style AgentLens example.

This example keeps the default path dependency-free so it works in CI and for first-time
users. If LangGraph is installed, it can be adapted to wrap these same node functions in a
StateGraph. The important AgentLens pattern is the same: trace each node and the workflow
entrypoint.
"""

from __future__ import annotations

from typing import TypedDict

from agentlens_ai import trace_agent, trace_tool


class AgentState(TypedDict, total=False):
    question: str
    route: str
    context: str
    answer: str


@trace_tool(name="route_question_node")
def route_question(state: AgentState) -> AgentState:
    question = state["question"]
    route = "pipeline_debug" if "pipeline" in question.lower() else "general_support"
    return {**state, "route": route}


@trace_tool(name="retrieve_context_node")
def retrieve_context(state: AgentState) -> AgentState:
    if state.get("route") == "pipeline_debug":
        context = "Check schema drift, freshness, dependencies, and recent deployment changes."
    else:
        context = "Collect symptoms, recent changes, and expected behavior."
    return {**state, "context": context}


@trace_tool(name="compose_answer_node")
def compose_answer(state: AgentState) -> AgentState:
    answer = f"Route: {state['route']}. Recommendation: {state['context']}"
    return {**state, "answer": answer}


def run_local_graph(initial_state: AgentState) -> AgentState:
    """Tiny local graph runner that mirrors a simple LangGraph node flow."""

    state = route_question(initial_state)
    state = retrieve_context(state)
    state = compose_answer(state)
    return state


@trace_agent(name="langgraph_style_agent")
def run_agent(question: str) -> str:
    final_state = run_local_graph({"question": question})
    return final_state["answer"]


if __name__ == "__main__":
    print(run_agent("Why did my data pipeline fail after deployment?"))
