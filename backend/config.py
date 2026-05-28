"""Gamma AI — Application Configuration via Pydantic BaseSettings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────
    app_name: str = "Gamma AI"
    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # ── Database ──────────────────────────────
    database_url: str = "postgresql+asyncpg://gamma_user:gamma_secret@localhost:5432/gamma_db"
    redis_url: str = "redis://localhost:6379/0"
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # ── Authentication ────────────────────────
    jwt_secret: str = "change-me-to-a-random-secret-string"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 720

    # ── OpenAI ────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # ── ElevenLabs ────────────────────────────
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "Rachel"

    # ── External APIs ─────────────────────────
    openweathermap_api_key: str = ""
    coingecko_api_key: str = ""
    news_api_key: str = ""

    # ── Memory TTLs (seconds) ─────────────────
    redis_short_term_ttl: int = 7200       # 2 hours
    redis_weather_cache_ttl: int = 1800    # 30 minutes
    redis_crypto_cache_ttl: int = 120      # 2 minutes
    redis_news_cache_ttl: int = 900        # 15 minutes

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()
