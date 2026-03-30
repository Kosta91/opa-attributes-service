"""Redis connection pool and FastAPI dependency."""

from redis.asyncio import Redis
from typing import AsyncGenerator

from app.redis.redis_settings import redis_settings

_redis_pool: Redis | None = None


def get_redis_pool() -> Redis:
    """Get or create Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = Redis.from_url(redis_settings.REDIS_URL, decode_responses=True)
    return _redis_pool


async def get_redis() -> AsyncGenerator[Redis | None, None]:
    """FastAPI dependency for Redis client. Yields None when Redis is disabled."""
    if not redis_settings.REDIS_ENABLED:
        yield None
        return
    yield get_redis_pool()
