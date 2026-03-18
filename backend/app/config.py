"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration — reads from .env or environment."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://aipulse:localdev@localhost:5433/aipulse"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # API
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "info"

    # External APIs
    GITHUB_TOKEN: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
