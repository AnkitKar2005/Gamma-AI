"""Gamma AI — Redis Short-Term Memory Store."""

import json
from typing import Optional

import structlog

from config import get_settings

logger = structlog.get_logger()


class RedisMemory:
    """Short-term memory using Redis with TTL-based expiration."""

    def __init__(self):
        self._redis = None

    async def connect(self, redis_url: Optional[str] = None) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as aioredis
            url = redis_url or get_settings().redis_url
            self._redis = aioredis.from_url(url, decode_responses=True)
            await self._redis.ping()
            await logger.ainfo("RedisMemory connected")
        except Exception as e:
            await logger.awarning("RedisMemory unavailable, using fallback", error=str(e))
            self._redis = None

    async def store_turn(self, session_id: str, role: str, content: str) -> None:
        """Store a conversation turn with TTL."""
        if self._redis is None:
            return
        try:
            settings = get_settings()
            key = f"gamma:turns:{session_id}"
            turn = json.dumps({"role": role, "content": content})
            await self._redis.rpush(key, turn)
            await self._redis.ltrim(key, -20, -1)  # Keep last 20 turns
            await self._redis.expire(key, settings.redis_short_term_ttl)
        except Exception as e:
            await logger.awarning("Failed to store turn", error=str(e))

    async def get_recent_turns(self, session_id: str, n: int = 10) -> list[dict]:
        """Get the last N conversation turns."""
        if self._redis is None:
            return []
        try:
            key = f"gamma:turns:{session_id}"
            raw_turns = await self._redis.lrange(key, -n, -1)
            return [json.loads(t) for t in raw_turns]
        except Exception as e:
            await logger.awarning("Failed to get turns", error=str(e))
            return []

    async def cache_set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set a cache value with TTL."""
        if self._redis is None:
            return
        try:
            await self._redis.set(f"gamma:cache:{key}", value, ex=ttl)
        except Exception as e:
            await logger.awarning("Cache set failed", error=str(e))

    async def cache_get(self, key: str) -> Optional[str]:
        """Get a cached value."""
        if self._redis is None:
            return None
        try:
            return await self._redis.get(f"gamma:cache:{key}")
        except Exception as e:
            await logger.awarning("Cache get failed", error=str(e))
            return None

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()


# Global singleton
redis_memory = RedisMemory()
