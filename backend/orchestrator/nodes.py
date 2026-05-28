"""Gamma AI — LangGraph Graph Node Functions."""

import structlog

from orchestrator.state import GammaState
from config import get_settings

logger = structlog.get_logger()


async def classify_intent(state: GammaState) -> dict:
    """Classify user intent using GPT-4o structured output.

    Intent labels: weather, crypto, news, memory_query, memory_store,
    decision, general, voice_command.
    """
    try:
        from services.llm import llm_service

        user_input = state["user_input"].lower()

        # Fast heuristic checks first (avoid LLM call for obvious intents)
        if any(w in user_input for w in ["weather", "temperature", "forecast", "rain", "sunny"]):
            return {"intent": "weather"}
        if any(w in user_input for w in ["bitcoin", "crypto", "btc", "eth", "price", "coin"]):
            return {"intent": "crypto"}
        if any(w in user_input for w in ["news", "headline", "article"]):
            return {"intent": "news"}
        if any(w in user_input for w in ["remember", "recall", "memory", "forget", "what do you know about me"]):
            return {"intent": "memory_query"}
        if any(w in user_input for w in ["decide", "should i", "recommend", "compare", "which is better"]):
            return {"intent": "decision"}

        # For ambiguous cases, use LLM classification
        if llm_service._client is not None:
            result = await llm_service.structured_output(
                messages=[
                    {"role": "system", "content": (
                        "Classify the user's intent into exactly one of: "
                        "weather, crypto, news, memory_query, memory_store, "
                        "decision, general, voice_command. "
                        "Respond with ONLY the label, nothing else."
                    )},
                    {"role": "user", "content": state["user_input"]},
                ],
            )
            if result and result.strip() in (
                "weather", "crypto", "news", "memory_query",
                "memory_store", "decision", "general", "voice_command"
            ):
                return {"intent": result.strip()}

        return {"intent": "general"}
    except Exception as e:
        await logger.aerror("Intent classification failed", error=str(e))
        return {"intent": "general"}


async def retrieve_memory(state: GammaState) -> dict:
    """Fan out to Redis → Chroma → Postgres, merge context."""
    memory_context = {
        "recent_turns": [],
        "semantic_matches": [],
        "user_profile": {},
    }

    try:
        from memory.redis_store import redis_memory

        # Get recent conversation turns from Redis
        turns = await redis_memory.get_recent_turns(state["session_id"])
        memory_context["recent_turns"] = turns
    except Exception as e:
        await logger.awarning("Redis memory retrieval failed", error=str(e))

    try:
        from memory.chroma_store import chroma_memory

        # Semantic search in ChromaDB
        matches = await chroma_memory.semantic_search(state["user_input"])
        memory_context["semantic_matches"] = matches
    except Exception as e:
        await logger.awarning("Chroma memory retrieval failed", error=str(e))

    try:
        from memory.postgres_store import postgres_memory

        # Get user profile from Postgres
        profile = await postgres_memory.get_user_profile(state["session_id"])
        memory_context["user_profile"] = profile or {}
    except Exception as e:
        await logger.awarning("Postgres memory retrieval failed", error=str(e))

    return {"memory_context": memory_context}


async def route_agent(state: GammaState) -> dict:
    """Route to the appropriate agent based on classified intent.

    Returns agent results that will be injected into the response context.
    """
    intent = state.get("intent", "general")
    agent_results = {}

    try:
        if intent == "weather":
            from agents.data_agent import data_agent
            result = await data_agent.execute(state)
            agent_results = result

        elif intent == "crypto":
            from agents.data_agent import data_agent
            result = await data_agent.execute(state)
            agent_results = result

        elif intent == "news":
            from agents.data_agent import data_agent
            result = await data_agent.execute(state)
            agent_results = result

        elif intent == "decision":
            from agents.decision_agent import decision_agent
            result = await decision_agent.execute(state)
            agent_results = result

        elif intent in ("memory_query", "memory_store"):
            from agents.memory_agent import memory_agent
            result = await memory_agent.execute(state)
            agent_results = result

        else:
            # General — no special agent, just generate response
            agent_results = {"type": "general"}

    except Exception as e:
        await logger.aerror("Agent routing failed", intent=intent, error=str(e))
        agent_results = {"error": str(e), "type": "fallback"}

    return {"agent_results": agent_results}


async def generate_response(state: GammaState) -> dict:
    """Generate streaming response using GPT-4o with full context injection."""
    try:
        from services.llm import llm_service

        # Build system prompt with memory context
        memory = state.get("memory_context", {})
        agent_results = state.get("agent_results", {})

        system_parts = [
            "You are Gamma AI, an intelligent AI operating system. "
            "You are helpful, concise, and proactive. "
            "You have access to the user's memory, preferences, and live data."
        ]

        # Inject memory context
        if memory.get("user_profile"):
            prefs = memory["user_profile"].get("preferences", {})
            if prefs:
                system_parts.append(f"User preferences: {prefs}")

        if memory.get("semantic_matches"):
            matches = memory["semantic_matches"][:3]
            context_str = "; ".join(str(m) for m in matches)
            system_parts.append(f"Relevant memories: {context_str}")

        # Inject agent results
        if agent_results and agent_results.get("type") != "general":
            system_parts.append(f"Live data: {agent_results}")

        system_prompt = "\n".join(system_parts)

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        history = state.get("conversation_history", [])
        messages.extend(history[-10:])  # Last 10 turns

        # Add current user input
        messages.append({"role": "user", "content": state["user_input"]})

        # Stream response
        tokens = []
        if llm_service._client is not None:
            async for token in llm_service.stream_chat(messages):
                tokens.append(token)
        else:
            # Fallback when OpenAI is not configured
            fallback = (
                f"I understood your message about '{state['user_input'][:50]}'. "
                f"AI streaming will be fully connected once the OpenAI API key is configured."
            )
            tokens = list(fallback)

        return {
            "response_tokens": tokens,
            "final_response": "".join(tokens),
        }
    except Exception as e:
        await logger.aerror("Response generation failed", error=str(e))
        return {
            "response_tokens": [],
            "final_response": f"I encountered an error: {e}. Please try again.",
            "error": str(e),
        }
