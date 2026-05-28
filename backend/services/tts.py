"""Gamma AI — ElevenLabs Text-to-Speech Service."""

import asyncio
from typing import AsyncGenerator

import structlog

from config import get_settings

logger = structlog.get_logger()


async def stream_tts(
    text: str,
    voice_id: str | None = None,
) -> AsyncGenerator[bytes, None]:
    """Stream TTS audio chunks from ElevenLabs.

    Args:
        text: Text to synthesize.
        voice_id: ElevenLabs voice ID (defaults to settings).

    Yields:
        Audio bytes chunks (mp3 format).
    """
    settings = get_settings()
    voice_id = voice_id or settings.elevenlabs_voice_id

    if not settings.elevenlabs_api_key:
        await logger.awarning("ElevenLabs API key not set — TTS unavailable")
        return

    try:
        import httpx

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

        # Split text into sentences for natural pauses
        sentences = _split_sentences(text)

        async with httpx.AsyncClient(timeout=30) as client:
            for sentence in sentences:
                if not sentence.strip():
                    continue

                response = await client.post(
                    url,
                    headers={
                        "xi-api-key": settings.elevenlabs_api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text": sentence,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                        },
                    },
                )
                response.raise_for_status()

                # Yield audio chunks
                chunk_size = 4096
                for i in range(0, len(response.content), chunk_size):
                    yield response.content[i : i + chunk_size]
                    await asyncio.sleep(0)  # Yield control

    except Exception as e:
        await logger.aerror("TTS streaming failed", error=str(e))


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences for natural TTS pausing."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sentences if s.strip()]
