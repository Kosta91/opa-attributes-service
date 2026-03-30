from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from app.cache.base import InMemoryAttributeStore
from app.redis.redis_settings import redis_settings


class RedisAttributeStore(InMemoryAttributeStore):
    """Cache backed by Redis."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, key: str, value: Any) -> None:
        await self._redis.set(key, json.dumps(value), ex=redis_settings.REDIS_CACHE_TTL)
