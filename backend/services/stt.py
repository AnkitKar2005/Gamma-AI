"""Gamma AI — Whisper Speech-to-Text Service."""

import structlog

from config import get_settings

logger = structlog.get_logger()


async def transcribe(audio_bytes: bytes, audio_format: str = "webm") -> str:
    """Transcribe audio bytes to text using OpenAI Whisper API.

    Args:
        audio_bytes: Raw audio data.
        audio_format: Audio format (webm, mp3, wav, etc.).

    Returns:
        Transcribed text string.
    """
    settings = get_settings()

    if not settings.openai_api_key:
        await logger.awarning("OpenAI API key not set — STT unavailable")
        return "[Voice transcription unavailable — configure OPENAI_API_KEY]"

    try:
        from openai import AsyncOpenAI
        import io

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = f"audio.{audio_format}"

        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )

        transcript = response.strip() if isinstance(response, str) else str(response)
        await logger.ainfo("Transcription complete", length=len(transcript))
        return transcript

    except Exception as e:
        await logger.aerror("Whisper transcription failed", error=str(e))
        raise
