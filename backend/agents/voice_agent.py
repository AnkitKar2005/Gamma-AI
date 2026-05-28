"""Gamma AI — Voice Agent (STT → Orchestrator → TTS Pipeline)."""

import asyncio
from typing import Any

import structlog

from agents.base import BaseAgent
from orchestrator.state import GammaState

logger = structlog.get_logger()


class VoiceAgent(BaseAgent):
    """Coordinates the voice pipeline: audio → STT → orchestrator → TTS → audio."""

    @property
    def name(self) -> str:
        return "voice_agent"

    def __init__(self):
        self._cancel_event = asyncio.Event()

    async def execute(self, state: GammaState) -> dict[str, Any]:
        """Process voice input through the pipeline."""
        return {"type": "voice", "agent": self.name}

    async def process_audio(
        self,
        audio_bytes: bytes,
        session_id: str,
        send_callback=None,
    ) -> dict[str, Any]:
        """Full voice pipeline: transcribe → orchestrate → synthesize.

        Args:
            audio_bytes: Raw audio from client.
            session_id: User session.
            send_callback: Async function to send WS messages back.
        """
        self._cancel_event.clear()
        results: dict[str, Any] = {"agent": self.name}

        # Step 1: Speech-to-Text
        try:
            from services.stt import transcribe
            transcript = await transcribe(audio_bytes)
            results["transcript"] = transcript
            await logger.ainfo("Voice transcribed", text=transcript[:50])
        except Exception as e:
            await logger.aerror("STT failed", error=str(e))
            results["error"] = f"Transcription failed: {e}"
            return results

        if self._cancel_event.is_set():
            return {"cancelled": True, **results}

        # Step 2: Run through orchestrator
        try:
            from orchestrator.graph import run_orchestrator
            state = await run_orchestrator(session_id, transcript)
            response_text = state.get("final_response", "")
            results["response"] = response_text
        except Exception as e:
            await logger.aerror("Orchestrator failed in voice pipeline", error=str(e))
            results["error"] = f"Processing failed: {e}"
            return results

        if self._cancel_event.is_set():
            return {"cancelled": True, **results}

        # Step 3: Text-to-Speech (streaming)
        try:
            from services.tts import stream_tts
            audio_chunks = []
            async for chunk in stream_tts(response_text):
                if self._cancel_event.is_set():
                    return {"cancelled": True, **results}
                audio_chunks.append(chunk)
                # Stream audio chunk back to client via callback
                if send_callback:
                    await send_callback(chunk)

            results["audio_chunks"] = len(audio_chunks)
        except Exception as e:
            await logger.aerror("TTS failed", error=str(e))
            results["tts_error"] = str(e)

        return results

    def cancel(self) -> None:
        """Cancel in-flight voice processing (barge-in)."""
        self._cancel_event.set()


# Global singleton
voice_agent = VoiceAgent()
