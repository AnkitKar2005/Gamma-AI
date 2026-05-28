"""Gamma AI — CoinGecko Crypto API Wrapper."""

from typing import Optional

import structlog
import httpx

from config import get_settings

logger = structlog.get_logger()

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


async def get_price(coin_id: str) -> Optional[dict]:
    """Get current price and market data for a coin."""
    settings = get_settings()

    # Check Redis cache
    try:
        from memory.redis_store import redis_memory
        cached = await redis_memory.cache_get(f"crypto:{coin_id}")
        if cached:
            import json
            return json.loads(cached)
    except Exception:
        pass

    try:
        headers = {}
        if settings.coingecko_api_key:
            headers["x-cg-demo-api-key"] = settings.coingecko_api_key

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{COINGECKO_BASE_URL}/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                },
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            if coin_id not in data:
                return {"coin": coin_id, "error": "Not found", "source": "coingecko"}

            coin_data = data[coin_id]
            result = {
                "coin": coin_id,
                "price": coin_data.get("usd", 0),
                "price_change_24h": coin_data.get("usd_24h_change", 0),
                "market_cap": coin_data.get("usd_market_cap", 0),
                "volume_24h": coin_data.get("usd_24h_vol", 0),
                "source": "coingecko",
            }

            # Cache result
            try:
                from memory.redis_store import redis_memory
                import json
                await redis_memory.cache_set(
                    f"crypto:{coin_id}",
                    json.dumps(result),
                    ttl=settings.redis_crypto_cache_ttl,
                )
            except Exception:
                pass

            return result
    except Exception as e:
        await logger.aerror("Crypto API error", coin=coin_id, error=str(e))
        # Return mock data on failure
        return {
            "coin": coin_id,
            "price": 67542.30 if coin_id == "bitcoin" else 3421.15,
            "price_change_24h": 2.3,
            "market_cap": 0,
            "volume_24h": 0,
            "source": "mock",
        }


async def get_market_data(coin_ids: list[str]) -> list[dict]:
    """Get market data for multiple coins."""
    import asyncio
    results = await asyncio.gather(
        *[get_price(c) for c in coin_ids],
        return_exceptions=True,
    )
    return [r for r in results if isinstance(r, dict)]
