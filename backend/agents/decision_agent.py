"""Gamma AI — Decision Agent."""

from typing import Any

import structlog

from agents.base import BaseAgent
from orchestrator.state import GammaState

logger = structlog.get_logger()


class DecisionAgent(BaseAgent):
    """Agent for multi-step reasoning and structured recommendations."""

    @property
    def name(self) -> str:
        return "decision_agent"

    async def execute(self, state: GammaState) -> dict[str, Any]:
        """Generate a structured decision with rationale."""
        try:
            from services.llm import llm_service

            user_input = state.get("user_input", "")
            memory_context = state.get("memory_context", {})

            system_prompt = (
                "You are a decision-making assistant. Analyze the user's question and provide "
                "a structured decision. Respond in this exact JSON format:\n"
                '{"recommendation": "your main recommendation",'
                '"rationale": "why you recommend this",'
                '"confidence": 0.85,'
                '"alternatives": ["alternative 1", "alternative 2"],'
                '"follow_up_suggestions": ["suggestion 1"]}\n'
                "Base confidence on how much information you have. "
                "If user preferences are available, factor them in."
            )

            # Inject memory context if available
            if memory_context.get("user_profile", {}).get("preferences"):
                prefs = memory_context["user_profile"]["preferences"]
                system_prompt += f"\n\nUser preferences: {prefs}"

            result = await llm_service.structured_output(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )

            if result:
                import json
                try:
                    decision = json.loads(result)
                    return {
                        "type": "decision",
                        "agent": self.name,
                        **decision,
                    }
                except json.JSONDecodeError:
                    return {
                        "type": "decision",
                        "agent": self.name,
                        "recommendation": result,
                        "confidence": 0.5,
                    }

            return {
                "type": "decision",
                "agent": self.name,
                "recommendation": "I need more information to make a good recommendation.",
                "confidence": 0.3,
            }

        except Exception as e:
            await logger.aerror("Decision agent failed", error=str(e))
            return {
                "type": "decision",
                "agent": self.name,
                "error": str(e),
            }


# Global singleton
decision_agent = DecisionAgent()
