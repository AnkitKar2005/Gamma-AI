"""Gamma AI — Data Agent (Weather, Crypto, News)."""

import asyncio
from typing import Any

import structlog

from agents.base import BaseAgent
from orchestrator.state import GammaState

logger = structlog.get_logger()


class DataAgent(BaseAgent):
    """Agent that fetches live data from external APIs."""

    @property
    def name(self) -> str:
        return "data_agent"

    async def execute(self, state: GammaState) -> dict[str, Any]:
        """Dispatch to appropriate data source based on intent."""
        intent = state.get("intent", "")
        user_input = state.get("user_input", "")
        results: dict[str, Any] = {"type": "data", "agent": self.name}

        try:
            if intent == "weather":
                from tools.weather import get_weather
                # Extract city from input (simple heuristic)
                city = self._extract_city(user_input) or "London"
                data = await get_weather(city)
                results["weather"] = data

            elif intent == "crypto":
                from tools.crypto import get_price
                coin = self._extract_coin(user_input) or "bitcoin"
                data = await get_price(coin)
                results["crypto"] = data

            elif intent == "news":
                from tools.news import get_headlines
                data = await get_headlines()
                results["news"] = data

            else:
                # Parallel fetch all
                tasks = []
                try:
                    from tools.weather import get_weather
                    tasks.append(("weather", get_weather("London")))
                except ImportError:
                    pass
                try:
                    from tools.crypto import get_price
                    tasks.append(("crypto", get_price("bitcoin")))
                except ImportError:
                    pass

                if tasks:
                    gathered = await asyncio.gather(
                        *[t[1] for t in tasks], return_exceptions=True
                    )
                    for (key, _), result in zip(tasks, gathered):
                        if not isinstance(result, Exception):
                            results[key] = result

        except Exception as e:
            await logger.aerror("Data agent failed", error=str(e))
            results["error"] = str(e)

        return results

    def _extract_city(self, text: str) -> str | None:
        """Simple city extraction from text."""
        words = text.lower().split()
        prepositions = {"in", "for", "at"}
        for i, word in enumerate(words):
            if word in prepositions and i + 1 < len(words):
                return words[i + 1].capitalize()
        return None

    def _extract_coin(self, text: str) -> str | None:
        """Extract cryptocurrency name from text."""
        coin_map = {
            "bitcoin": "bitcoin", "btc": "bitcoin",
            "ethereum": "ethereum", "eth": "ethereum",
            "solana": "solana", "sol": "solana",
            "dogecoin": "dogecoin", "doge": "dogecoin",
            "cardano": "cardano", "ada": "cardano",
        }
        lower = text.lower()
        for keyword, coin_id in coin_map.items():
            if keyword in lower:
                return coin_id
        return None


# Global singleton
data_agent = DataAgent()
