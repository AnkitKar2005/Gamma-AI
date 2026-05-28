"""Gamma AI — Redis Pub/Sub Event Bus for cross-component communication."""

import asyncio
import json
from typing import Callable, Optional

import structlog

from models.schemas import WSMessage

logger = structlog.get_logger()

# Event channels
CHANNEL_AGENT_EVENTS = "gamma:agent_events"
CHANNEL_NOTIFICATIONS = "gamma:notifications"
CHANNEL_MEMORY_UPDATES = "gamma:memory_updates"


class EventBus:
    """Redis pub/sub event bus for background agent → WebSocket forwarding.

    Falls back to an in-memory asyncio.Queue when Redis is unavailable.
    """

    def __init__(self):
        self._redis = None
        self._pubsub = None
        self._subscribers: dict[str, list[Callable]] = {}
        self._listen_task: Optional[asyncio.Task] = None
        self._local_queues: dict[str, asyncio.Queue] = {}
        self._use_redis = False

    async def connect(self, redis_url: str) -> None:
        """Connect to Redis for pub/sub."""
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(redis_url, decode_responses=True)
            await self._redis.ping()
            self._pubsub = self._redis.pubsub()
            self._use_redis = True
            await logger.ainfo("EventBus connected to Redis")
        except Exception as e:
            await logger.awarning("EventBus falling back to in-memory mode", error=str(e))
            self._use_redis = False

    async def publish(self, channel: str, event: dict) -> None:
        """Publish an event to a channel."""
        payload = json.dumps(event, default=str)

        if self._use_redis and self._redis:
            try:
                await self._redis.publish(channel, payload)
                return
            except Exception as e:
                await logger.awarning("Redis publish failed, using local", error=str(e))

        # Fallback: local queue
        if channel not in self._local_queues:
            self._local_queues[channel] = asyncio.Queue()
        await self._local_queues[channel].put(event)

    async def subscribe(self, channel: str, callback: Callable) -> None:
        """Subscribe to a channel with a callback function."""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)

        if self._use_redis and self._pubsub:
            await self._pubsub.subscribe(channel)
            # Start listen loop if not running
            if self._listen_task is None or self._listen_task.done():
                self._listen_task = asyncio.create_task(self._redis_listen_loop())
        else:
            # Start local listen loop
            if channel not in self._local_queues:
                self._local_queues[channel] = asyncio.Queue()
            asyncio.create_task(self._local_listen_loop(channel))

    async def _redis_listen_loop(self) -> None:
        """Listen for Redis pub/sub messages and dispatch to subscribers."""
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    try:
                        data = json.loads(message["data"])
                    except json.JSONDecodeError:
                        data = {"raw": message["data"]}

                    callbacks = self._subscribers.get(channel, [])
                    for cb in callbacks:
                        try:
                            await cb(data)
                        except Exception as e:
                            await logger.aerror("Subscriber error", channel=channel, error=str(e))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            await logger.aerror("Redis listen loop error", error=str(e))

    async def _local_listen_loop(self, channel: str) -> None:
        """Fallback: listen on local asyncio.Queue."""
        queue = self._local_queues[channel]
        try:
            while True:
                data = await queue.get()
                callbacks = self._subscribers.get(channel, [])
                for cb in callbacks:
                    try:
                        await cb(data)
                    except Exception as e:
                        await logger.aerror("Local subscriber error", channel=channel, error=str(e))
        except asyncio.CancelledError:
            pass

    async def close(self) -> None:
        """Clean up connections."""
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()


# Global singleton
event_bus = EventBus()
