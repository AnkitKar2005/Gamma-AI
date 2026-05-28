"""Gamma AI — NewsAPI Wrapper."""

from typing import Optional

import structlog
import httpx

from config import get_settings

logger = structlog.get_logger()

NEWS_BASE_URL = "https://newsapi.org/v2"


async def get_headlines(
    category: str = "technology",
    country: str = "us",
    page_size: int = 5,
) -> list[dict]:
    """Get top headlines."""
    settings = get_settings()

    # Check Redis cache
    cache_key = f"news:{category}:{country}"
    try:
        from memory.redis_store import redis_memory
        cached = await redis_memory.cache_get(cache_key)
        if cached:
            import json
            return json.loads(cached)
    except Exception:
        pass

    if not settings.news_api_key:
        # Return mock data
        return [
            {
                "title": "AI Advances: New Language Models Show Promising Results",
                "description": "Recent developments in AI research continue to push boundaries.",
                "source": "mock",
                "url": "#",
                "published_at": "2024-01-01T00:00:00Z",
            },
            {
                "title": "Tech Industry Sees Record Growth in Q4",
                "description": "Major tech companies report strong earnings.",
                "source": "mock",
                "url": "#",
                "published_at": "2024-01-01T00:00:00Z",
            },
        ]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{NEWS_BASE_URL}/top-headlines",
                params={
                    "category": category,
                    "country": country,
                    "pageSize": page_size,
                    "apiKey": settings.news_api_key,
                },
            )
            response.raise_for_status()
            data = response.json()

            articles = [
                {
                    "title": a.get("title", ""),
                    "description": a.get("description", ""),
                    "source": a.get("source", {}).get("name", "Unknown"),
                    "url": a.get("url", ""),
                    "published_at": a.get("publishedAt", ""),
                }
                for a in data.get("articles", [])
            ]

            # Cache result
            try:
                from memory.redis_store import redis_memory
                import json
                await redis_memory.cache_set(
                    cache_key,
                    json.dumps(articles),
                    ttl=settings.redis_news_cache_ttl,
                )
            except Exception:
                pass

            return articles
    except Exception as e:
        await logger.aerror("News API error", error=str(e))
        return []


async def search_news(query: str, page_size: int = 5) -> list[dict]:
    """Search news articles by query."""
    settings = get_settings()

    if not settings.news_api_key:
        return [{"title": f"Mock result for '{query}'", "source": "mock", "url": "#"}]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{NEWS_BASE_URL}/everything",
                params={
                    "q": query,
                    "pageSize": page_size,
                    "sortBy": "relevancy",
                    "apiKey": settings.news_api_key,
                },
            )
            response.raise_for_status()
            data = response.json()

            return [
                {
                    "title": a.get("title", ""),
                    "description": a.get("description", ""),
                    "source": a.get("source", {}).get("name", "Unknown"),
                    "url": a.get("url", ""),
                    "published_at": a.get("publishedAt", ""),
                }
                for a in data.get("articles", [])
            ]
    except Exception as e:
        await logger.aerror("News search error", query=query, error=str(e))
        return []
