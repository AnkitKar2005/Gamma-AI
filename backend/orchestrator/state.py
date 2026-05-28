"""Gamma AI — LangGraph Orchestrator State Schema."""

from typing import Optional, TypedDict


class GammaState(TypedDict):
    """State schema for the LangGraph orchestrator.

    Every node in the graph reads/writes to this shared state.
    """

    # ── Input ─────────────────────────────
    session_id: str
    user_input: str

    # ── Classification ────────────────────
    intent: str                           # classified intent label

    # ── Memory Context ────────────────────
    memory_context: dict                  # merged memory from all tiers

    # ── Agent Results ─────────────────────
    agent_results: dict                   # results from dispatched agents

    # ── Response ──────────────────────────
    response_tokens: list[str]            # streaming tokens
    final_response: str                   # assembled full response

    # ── Conversation History ──────────────
    conversation_history: list[dict]      # [{"role": "user"/"assistant", "content": "..."}]

    # ── Error Handling ────────────────────
    error: Optional[str]

    # ── Metadata ──────────────────────────
    metadata: dict                        # arbitrary key-value context
