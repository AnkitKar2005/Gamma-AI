"""Gamma AI — OpenWeatherMap API Wrapper."""

from typing import Optional

import structlog
import httpx

from config import get_settings

logger = structlog.get_logger()

WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


async def get_weather(city: str) -> Optional[dict]:
    """Get current weather for a city."""
    settings = get_settings()

    # Check Redis cache first
    try:
        from memory.redis_store import redis_memory
        cached = await redis_memory.cache_get(f"weather:{city.lower()}")
        if cached:
            import json
            return json.loads(cached)
    except Exception:
        pass

    if not settings.openweathermap_api_key:
        # Return mock data when API key isn't configured
        return {
            "city": city,
            "temperature": 22,
            "feels_like": 20,
            "condition": "Partly Cloudy",
            "humidity": 65,
            "wind_speed": 12,
            "icon": "02d",
            "source": "mock",
        }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{WEATHER_BASE_URL}/weather",
                params={
                    "q": city,
                    "appid": settings.openweathermap_api_key,
                    "units": "metric",
                },
            )
            response.raise_for_status()
            data = response.json()

            result = {
                "city": data.get("name", city),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "condition": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "icon": data["weather"][0]["icon"],
                "source": "openweathermap",
            }

            # Cache result
            try:
                from memory.redis_store import redis_memory
                import json
                await redis_memory.cache_set(
                    f"weather:{city.lower()}",
                    json.dumps(result),
                    ttl=settings.redis_weather_cache_ttl,
                )
            except Exception:
                pass

            return result
    except Exception as e:
        await logger.aerror("Weather API error", city=city, error=str(e))
        return None


async def get_forecast(city: str, days: int = 3) -> Optional[list[dict]]:
    """Get weather forecast for a city."""
    settings = get_settings()

    if not settings.openweathermap_api_key:
        return [
            {"day": f"Day {i+1}", "temp": 20 + i, "condition": "Sunny", "source": "mock"}
            for i in range(days)
        ]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{WEATHER_BASE_URL}/forecast",
                params={
                    "q": city,
                    "appid": settings.openweathermap_api_key,
                    "units": "metric",
                    "cnt": days * 8,  # 3-hour intervals
                },
            )
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for item in data.get("list", [])[:days]:
                forecasts.append({
                    "datetime": item["dt_txt"],
                    "temp": item["main"]["temp"],
                    "condition": item["weather"][0]["description"],
                    "source": "openweathermap",
                })
            return forecasts
    except Exception as e:
        await logger.aerror("Forecast API error", city=city, error=str(e))
        return None
