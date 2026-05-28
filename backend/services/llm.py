"""Gamma AI — OpenAI LLM Service Wrapper."""

from typing import AsyncGenerator, Optional

import structlog

from config import get_settings

logger = structlog.get_logger()


class LLMService:
    """Wrapper around OpenAI AsyncClient for chat, structured output, and embeddings."""

    def __init__(self):
        self._client = None
        self._settings = None

    async def initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import AsyncOpenAI

            self._settings = get_settings()
            if not self._settings.openai_api_key:
                await logger.awarning("OpenAI API key not set — LLM service in fallback mode")
                return

            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)
            await logger.ainfo("LLM service initialized", model=self._settings.openai_model)
        except Exception as e:
            await logger.aerror("LLM service init failed", error=str(e))

    async def stream_chat(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion tokens."""
        if self._client is None:
            yield f"[LLM not configured — set OPENAI_API_KEY]"
            return

        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = await self._client.chat.completions.create(
                model=model or self._settings.openai_model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2048,
            )

            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except Exception as e:
            await logger.aerror("Stream chat failed", error=str(e))
            yield f"[Error: {e}]"

    async def structured_output(
        self,
        messages: list[dict],
        model: Optional[str] = None,
    ) -> Optional[str]:
        """Get a single completion (non-streaming) for structured output."""
        if self._client is None:
            return None

        try:
            response = await self._client.chat.completions.create(
                model=model or self._settings.openai_model,
                messages=messages,
                temperature=0.0,
                max_tokens=256,
            )
            return response.choices[0].message.content
        except Exception as e:
            await logger.aerror("Structured output failed", error=str(e))
            return None

    async def embed(self, text: str) -> Optional[list[float]]:
        """Generate an embedding vector for the given text."""
        if self._client is None:
            return None

        try:
            response = await self._client.embeddings.create(
                model=self._settings.openai_embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            await logger.aerror("Embedding failed", error=str(e))
            return None


# Global singleton
llm_service = LLMService()
