"""Gamma AI — WebSocket Message Handler / Dispatcher."""

import structlog
from fastapi import WebSocket, WebSocketDisconnect

from models.schemas import WSMessage, WSMessageType
from websocket.manager import ConnectionManager

logger = structlog.get_logger()


class MessageHandler:
    """Dispatches incoming WebSocket messages to the appropriate handlers."""

    def __init__(self, manager: ConnectionManager):
        self._manager = manager
        # Handler registry: message type → async handler function
        self._handlers: dict[WSMessageType, list] = {}

    def on(self, msg_type: WSMessageType, handler) -> None:
        """Register a handler for a message type."""
        if msg_type not in self._handlers:
            self._handlers[msg_type] = []
        self._handlers[msg_type].append(handler)

    async def handle_connection(self, websocket: WebSocket, session_id: str) -> None:
        """Main loop: receive messages and dispatch to handlers."""
        await self._manager.connect(websocket, session_id)

        try:
            while True:
                raw = await websocket.receive_json()
                await self._dispatch(raw, session_id)
        except WebSocketDisconnect:
            await logger.ainfo("Client disconnected", session_id=session_id)
        except Exception as e:
            await logger.aerror("WebSocket error", session_id=session_id, error=str(e))
            await self._manager.send_error(session_id, str(e))
        finally:
            await self._manager.disconnect(session_id)

    async def _dispatch(self, raw: dict, session_id: str) -> None:
        """Parse and dispatch a raw message."""
        try:
            # Validate with Pydantic
            message = WSMessage(**raw, session_id=session_id)
        except Exception as e:
            await logger.awarning("Invalid WS message", error=str(e), raw=raw)
            await self._manager.send_error(session_id, f"Invalid message format: {e}")
            return

        msg_type = message.type

        # Handle heartbeat (pong) immediately
        if msg_type == WSMessageType.HEARTBEAT:
            self._manager.record_pong(session_id)
            return

        # Handle ACK immediately
        if msg_type == WSMessageType.ACK:
            await logger.adebug("ACK received", session_id=session_id, ack_id=message.payload.get("ack_id"))
            return

        # Handle Interrupt (Barge-in)
        if msg_type == WSMessageType.INTERRUPT:
            from agents.voice_agent import voice_agent
            voice_agent.cancel()
            await logger.ainfo("Voice interrupt received", session_id=session_id)
            return

        # Handle voice data
        if msg_type == WSMessageType.VOICE_DATA:
            await self._handle_voice(message, session_id)
            return

        # Send ACK for non-system messages
        if msg_type not in (WSMessageType.HEARTBEAT, WSMessageType.ACK):
            await self._manager.send_ack(session_id, message.id)

        # Dispatch to registered handlers
        handlers = self._handlers.get(msg_type, [])
        if not handlers:
            await logger.awarning("No handler for message type", type=msg_type, session_id=session_id)
            # Phase 1-2: echo back for unhandled message types
            await self._handle_echo(message, session_id)
            return

        for handler in handlers:
            try:
                await handler(message, session_id)
            except Exception as e:
                await logger.aerror(
                    "Handler error",
                    type=msg_type,
                    session_id=session_id,
                    error=str(e),
                )
                await self._manager.send_error(session_id, f"Handler error: {e}", message.id)

    async def _handle_voice(self, message: WSMessage, session_id: str) -> None:
        """Process incoming voice audio chunks."""
        try:
            import base64
            from agents.voice_agent import voice_agent

            audio_base64 = message.payload.get("audio", "")
            if not audio_base64:
                return

            audio_bytes = base64.b64decode(audio_base64)

            # Callback to stream audio chunks back if TTS generates them
            async def send_audio_chunk(chunk_bytes: bytes):
                chunk_b64 = base64.b64encode(chunk_bytes).decode("utf-8")
                msg = WSMessage(
                    session_id=session_id,
                    type=WSMessageType.VOICE_DATA,
                    payload={"audio": chunk_b64}
                )
                await self._manager.send_to_session(session_id, msg)

            # Note: In a production app, we would accumulate chunks or use a streaming STT.
            # Here we demonstrate the pipeline.
            await voice_agent.process_audio(
                audio_bytes=audio_bytes,
                session_id=session_id,
                send_callback=send_audio_chunk
            )

        except Exception as e:
            await logger.aerror("Voice processing failed", error=str(e))
            await self._manager.send_error(session_id, f"Voice error: {e}")

    async def _handle_echo(self, message: WSMessage, session_id: str) -> None:
        """Default echo handler for unregistered message types (dev/testing)."""
        if message.type == WSMessageType.CHAT_MESSAGE:
            # Echo the chat message back as an assistant response
            user_text = message.payload.get("content", "")
            response = WSMessage(
                session_id=session_id,
                type=WSMessageType.CHAT_TOKEN,
                payload={
                    "content": f"👋 Gamma AI received: \"{user_text}\". "
                               f"AI orchestration will be live in Phase 3.",
                    "message_id": message.id,
                },
            )
            await self._manager.send_to_session(session_id, response)

            # Send chat_done
            done = WSMessage(
                session_id=session_id,
                type=WSMessageType.CHAT_DONE,
                payload={"message_id": message.id},
            )
            await self._manager.send_to_session(session_id, done)
        else:
            await logger.adebug("Unhandled message type", type=message.type)
