"""Gamma AI — WebSocket Connection Manager."""

import asyncio
import time
from typing import Optional

import structlog
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from models.schemas import WSMessage, WSMessageType

logger = structlog.get_logger()


class ConnectionManager:
    """Manages active WebSocket connections with heartbeat and cleanup."""

    def __init__(self, heartbeat_interval: int = 30, stale_timeout: int = 90):
        self._connections: dict[str, WebSocket] = {}
        self._last_pong: dict[str, float] = {}
        self._heartbeat_interval = heartbeat_interval
        self._stale_timeout = stale_timeout
        self._lock = asyncio.Lock()
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            # Close existing connection for same session (reconnect)
            if session_id in self._connections:
                old = self._connections[session_id]
                try:
                    await old.close(code=4000, reason="Replaced by new connection")
                except Exception:
                    pass
            self._connections[session_id] = websocket
            self._last_pong[session_id] = time.time()

        await logger.ainfo("WebSocket connected", session_id=session_id, total=len(self._connections))

        # Start heartbeat if not running
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def disconnect(self, session_id: str) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            self._connections.pop(session_id, None)
            self._last_pong.pop(session_id, None)
        await logger.ainfo("WebSocket disconnected", session_id=session_id, total=len(self._connections))

    async def send_to_session(self, session_id: str, message: WSMessage) -> bool:
        """Send a typed message to a specific session."""
        ws = self._connections.get(session_id)
        if ws is None or ws.client_state != WebSocketState.CONNECTED:
            return False
        try:
            await ws.send_json(message.model_dump(mode="json"))
            return True
        except (WebSocketDisconnect, RuntimeError) as e:
            await logger.awarning("Send failed, removing connection", session_id=session_id, error=str(e))
            await self.disconnect(session_id)
            return False

    async def broadcast(self, message: WSMessage) -> int:
        """Send a message to all connected clients. Returns count of successful sends."""
        sent = 0
        session_ids = list(self._connections.keys())
        for sid in session_ids:
            if await self.send_to_session(sid, message):
                sent += 1
        return sent

    async def send_ack(self, session_id: str, message_id: str) -> None:
        """Send an acknowledgment for a received message."""
        ack = WSMessage(
            session_id=session_id,
            type=WSMessageType.ACK,
            payload={"ack_id": message_id},
        )
        await self.send_to_session(session_id, ack)

    async def send_error(self, session_id: str, error: str, message_id: str = "") -> None:
        """Send an error message to a session."""
        err = WSMessage(
            session_id=session_id,
            type=WSMessageType.ERROR,
            payload={"error": error, "ref_id": message_id},
        )
        await self.send_to_session(session_id, err)

    def record_pong(self, session_id: str) -> None:
        """Record a pong from a client."""
        self._last_pong[session_id] = time.time()

    @property
    def active_connections(self) -> int:
        """Number of active connections."""
        return len(self._connections)

    @property
    def session_ids(self) -> list[str]:
        """List of connected session IDs."""
        return list(self._connections.keys())

    async def _heartbeat_loop(self) -> None:
        """Send heartbeats and disconnect stale connections."""
        while self._connections:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                now = time.time()
                stale = []

                async with self._lock:
                    for sid, last in list(self._last_pong.items()):
                        if now - last > self._stale_timeout:
                            stale.append(sid)

                # Disconnect stale connections
                for sid in stale:
                    await logger.awarning("Disconnecting stale connection", session_id=sid)
                    ws = self._connections.get(sid)
                    if ws:
                        try:
                            await ws.close(code=4002, reason="Heartbeat timeout")
                        except Exception:
                            pass
                    await self.disconnect(sid)

                # Send heartbeat to remaining connections
                heartbeat = WSMessage(
                    session_id="server",
                    type=WSMessageType.HEARTBEAT,
                    payload={"server_time": now},
                )
                for sid in list(self._connections.keys()):
                    await self.send_to_session(sid, heartbeat)

            except asyncio.CancelledError:
                break
            except Exception as e:
                await logger.aerror("Heartbeat error", error=str(e))


# Global singleton
manager = ConnectionManager()
