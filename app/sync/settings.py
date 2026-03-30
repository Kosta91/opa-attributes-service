"""Configuration for the background sync worker."""

from pydantic_settings import BaseSettings


class SyncSettings(BaseSettings):
    SYNC_ENABLED: bool = True
    SYNC_INTERVAL_SECONDS: int = 1800
    SYNC_BATCH_SIZE: int = 50

    class Config:
        env_file = ".env"
        extra = "ignore"


sync_settings = SyncSettings()
