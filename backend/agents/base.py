"""Gamma AI — Abstract Base Agent."""

from abc import ABC, abstractmethod
from typing import Any

import structlog

from orchestrator.state import GammaState

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Abstract base class for all Gamma AI agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name identifier."""
        ...

    @abstractmethod
    async def execute(self, state: GammaState) -> dict[str, Any]:
        """Execute the agent's logic.

        Args:
            state: The current orchestrator state.

        Returns:
            Dict of results to merge into state["agent_results"].
        """
        ...

    async def safe_execute(self, state: GammaState) -> dict[str, Any]:
        """Execute with error handling and structured logging."""
        await logger.ainfo(f"Agent [{self.name}] executing", intent=state.get("intent"))
        try:
            result = await self.execute(state)
            await logger.ainfo(f"Agent [{self.name}] completed", result_keys=list(result.keys()))
            return result
        except Exception as e:
            await logger.aerror(f"Agent [{self.name}] failed", error=str(e))
            return {
                "error": str(e),
                "agent": self.name,
                "type": "error",
            }
