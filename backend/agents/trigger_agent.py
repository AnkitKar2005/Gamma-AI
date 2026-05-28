"""Gamma AI — Trigger Agent (Proactive Notifications)."""

from typing import Any

import structlog

from agents.base import BaseAgent
from orchestrator.state import GammaState

logger = structlog.get_logger()


class TriggerAgent(BaseAgent):
    """Monitors external signals and emits proactive notifications."""

    @property
    def name(self) -> str:
        return "trigger_agent"

    async def execute(self, state: GammaState) -> dict[str, Any]:
        """Not typically called via orchestrator — runs on scheduler."""
        return {"type": "trigger", "agent": self.name}

    async def check_crypto_volatility(self) -> list[dict]:
        """Check for significant crypto price movements."""
        alerts = []
        try:
            from tools.crypto import get_price

            coins = ["bitcoin", "ethereum"]
            for coin in coins:
                data = await get_price(coin)
                if data and isinstance(data, dict):
                    change = data.get("price_change_24h", 0)
                    if abs(change) > 5:
                        alerts.append({
                            "type": "crypto_volatility",
                            "title": f"{'📈' if change > 0 else '📉'} {coin.title()} moved {change:+.1f}%",
                            "body": f"Current price: ${data.get('price', 'N/A'):,.2f}",
                            "priority": "warning" if abs(change) > 10 else "info",
                        })
        except Exception as e:
            await logger.awarning("Crypto volatility check failed", error=str(e))
        return alerts

    async def check_weather_alerts(self, city: str = "London") -> list[dict]:
        """Check for weather alerts."""
        alerts = []
        try:
            from tools.weather import get_weather

            data = await get_weather(city)
            if data and isinstance(data, dict):
                condition = data.get("condition", "").lower()
                if any(w in condition for w in ["rain", "storm", "thunder", "snow"]):
                    alerts.append({
                        "type": "weather_alert",
                        "title": f"🌧️ Weather alert for {city}",
                        "body": f"Expect {condition}. Consider bringing an umbrella!",
                        "priority": "info",
                    })
        except Exception as e:
            await logger.awarning("Weather alert check failed", error=str(e))
        return alerts

    async def run_all_checks(self) -> list[dict]:
        """Run all trigger checks and return consolidated alerts."""
        import asyncio

        results = await asyncio.gather(
            self.check_crypto_volatility(),
            self.check_weather_alerts(),
            return_exceptions=True,
        )

        alerts = []
        for result in results:
            if isinstance(result, list):
                alerts.extend(result)
        return alerts


# Global singleton
trigger_agent = TriggerAgent()
