from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisSettings(BaseSettings):
    """Redis-specific configuration for streams, channels, and caches."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL (e.g., redis://localhost:6379/0)",
    )
    
redis_settings = RedisSettings()