from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AI_RESEARCH_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "ai-research-agent"
    version: str = "0.1.0"

    database_url: str | None = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai-research-agent"
    )
    database_check_timeout: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
