"""Redis connection settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisSettings(BaseSettings):
    """Redis-specific configuration for streams, channels, and caches."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    
    REDIS_ENABLED: bool = Field(
        default=False,
        description="Enable Redis as cache backend. When False, local in-memory cache is used.",
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL (e.g., redis://localhost:6379/0)",
    )
    REDIS_CACHE_TTL: int = Field(
        default=3600,
        description="Default cache TTL in seconds.",
    )

redis_settings = RedisSettings()