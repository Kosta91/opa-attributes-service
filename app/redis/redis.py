from redis.asyncio import Redis
from typing import AsyncGenerator

from app.redis.redis_settings import redis_settings

def get_redis_pool() -> Redis:
    """Get or create Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = Redis.from_url(redis_settings.REDIS_URL, decode_responses=True)
    return _redis_pool


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Dependency for Redis client in FastAPI endpoints.
    
    Usage in API routes:
        @router.get("/example")
        async def example(redis: Redis = Depends(get_redis)):
            await redis.set("key", "value")
    """
    redis = get_redis_pool()
    try:
        yield redis
    finally:
        # Connection pool managed by Redis client, no need to close per request
        pass