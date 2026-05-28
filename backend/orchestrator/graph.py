"""Gamma AI — LangGraph State Machine Definition."""

import structlog

from langgraph.graph import END, START, StateGraph

from orchestrator.state import GammaState
from orchestrator.nodes import (
    classify_intent,
    generate_response,
    retrieve_memory,
    route_agent,
)

logger = structlog.get_logger()


def _route_by_intent(state: GammaState) -> str:
    """Conditional edge: route to agent node or straight to response."""
    intent = state.get("intent", "general")
    if intent in ("weather", "crypto", "news", "memory_query", "memory_store", "decision"):
        return "route_agent"
    return "generate_response"


def build_graph() -> StateGraph:
    """Build the LangGraph orchestrator state machine.

    Flow:
        START → classify_intent → retrieve_memory → [conditional]
            ├── route_agent → generate_response → END
            └── generate_response → END
    """
    graph = StateGraph(GammaState)

    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_memory", retrieve_memory)
    graph.add_node("route_agent", route_agent)
    graph.add_node("generate_response", generate_response)

    # Define edges
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "retrieve_memory")

    # Conditional routing after memory retrieval
    graph.add_conditional_edges(
        "retrieve_memory",
        _route_by_intent,
        {
            "route_agent": "route_agent",
            "generate_response": "generate_response",
        },
    )

    # Agent → response → end
    graph.add_edge("route_agent", "generate_response")
    graph.add_edge("generate_response", END)

    return graph


# Compiled graph singleton
_compiled_graph = None


def get_orchestrator():
    """Get the compiled LangGraph orchestrator."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_graph()
        _compiled_graph = graph.compile()
    return _compiled_graph


async def run_orchestrator(session_id: str, user_input: str, history: list[dict] | None = None) -> dict:
    """Run the orchestrator pipeline and return the final state.

    Args:
        session_id: The user's session ID.
        user_input: The user's message.
        history: Optional conversation history.

    Returns:
        Final GammaState dict with response_tokens and final_response.
    """
    orchestrator = get_orchestrator()

    initial_state: GammaState = {
        "session_id": session_id,
        "user_input": user_input,
        "intent": "",
        "memory_context": {},
        "agent_results": {},
        "response_tokens": [],
        "final_response": "",
        "conversation_history": history or [],
        "error": None,
        "metadata": {},
    }

    try:
        result = await orchestrator.ainvoke(initial_state)
        return result
    except Exception as e:
        await logger.aerror("Orchestrator failed", error=str(e))
        return {
            **initial_state,
            "final_response": f"I encountered an error processing your request: {e}",
            "error": str(e),
        }
