from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """Database connection and pool configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    DATABASE_URL: str
    DB_POOL_SIZE: int = Field(default=10, ge=1)
    DB_MAX_OVERFLOW: int = Field(default=20, ge=0)
    DB_POOL_TIMEOUT: int = Field(default=10, ge=1)
    DB_POOL_RECYCLE: int = Field(default=1800, ge=60)
    DEBUG_SQL: bool = Field(default=False)


db_settings = DBSettings()
