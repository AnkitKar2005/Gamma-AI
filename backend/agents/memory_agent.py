"""Gamma AI — Memory Agent."""

from typing import Any

import structlog

from agents.base import BaseAgent
from orchestrator.state import GammaState

logger = structlog.get_logger()


class MemoryAgent(BaseAgent):
    """Agent responsible for memory storage, retrieval, and preference detection."""

    @property
    def name(self) -> str:
        return "memory_agent"

    async def execute(self, state: GammaState) -> dict[str, Any]:
        """Process memory operations based on intent."""
        intent = state.get("intent", "")
        user_input = state.get("user_input", "")
        session_id = state.get("session_id", "")
        results: dict[str, Any] = {"type": "memory", "agent": self.name}

        # Store the current turn in short-term memory
        await self._store_turn(session_id, user_input)

        # Detect and store preferences
        await self._detect_preferences(session_id, user_input)

        if intent == "memory_query":
            # Retrieve memories
            memories = await self._retrieve_memories(session_id, user_input)
            results["memories"] = memories
            results["summary"] = self._summarize_memories(memories)
        elif intent == "memory_store":
            # Explicitly store a memory
            await self._store_memory(session_id, user_input)
            results["stored"] = True
            results["summary"] = "Memory stored successfully."

        return results

    async def _store_turn(self, session_id: str, content: str) -> None:
        """Store conversation turn in Redis."""
        try:
            from memory.redis_store import redis_memory
            await redis_memory.store_turn(session_id, "user", content)
        except Exception as e:
            await logger.awarning("Failed to store turn", error=str(e))

    async def _detect_preferences(self, session_id: str, content: str) -> None:
        """Detect user preferences from the message content."""
        try:
            from services.llm import llm_service

            if llm_service._client is None:
                return

            result = await llm_service.structured_output(
                messages=[
                    {"role": "system", "content": (
                        "Analyze the user message for preferences or personal facts. "
                        "If found, respond with JSON: {\"key\": \"preference_name\", \"value\": \"preference_value\"}. "
                        "If no preference is found, respond with: null"
                    )},
                    {"role": "user", "content": content},
                ],
            )

            if result and result.strip() != "null":
                import json
                try:
                    pref = json.loads(result)
                    if isinstance(pref, dict) and "key" in pref and "value" in pref:
                        from memory.postgres_store import postgres_memory
                        await postgres_memory.update_preference(session_id, pref["key"], pref["value"])
                        await logger.ainfo("Preference detected", key=pref["key"], value=pref["value"])
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            await logger.awarning("Preference detection failed", error=str(e))

    async def _retrieve_memories(self, session_id: str, query: str) -> list[dict]:
        """Retrieve memories from all tiers."""
        memories = []

        try:
            from memory.redis_store import redis_memory
            turns = await redis_memory.get_recent_turns(session_id)
            memories.extend([{"source": "recent", **t} for t in turns])
        except Exception:
            pass

        try:
            from memory.chroma_store import chroma_memory
            semantic = await chroma_memory.semantic_search(query, top_k=5)
            memories.extend([{"source": "semantic", **m} for m in semantic])
        except Exception:
            pass

        return memories

    async def _store_memory(self, session_id: str, content: str) -> None:
        """Explicitly store a memory in ChromaDB."""
        try:
            from memory.chroma_store import chroma_memory
            await chroma_memory.embed_and_store(
                text=content,
                metadata={"session_id": session_id, "type": "explicit"},
            )
        except Exception as e:
            await logger.awarning("Failed to store explicit memory", error=str(e))

    def _summarize_memories(self, memories: list[dict]) -> str:
        """Create a brief summary of retrieved memories."""
        if not memories:
            return "No memories found."
        count = len(memories)
        sources = set(m.get("source", "unknown") for m in memories)
        return f"Found {count} memories from: {', '.join(sources)}"


# Global singleton
memory_agent = MemoryAgent()
