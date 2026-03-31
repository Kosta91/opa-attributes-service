"""Local in-process LRU cache implementation of InMemoryAttributeStore."""

from __future__ import annotations


from cachetools import LRUCache
from typing import Any

from app.cache.base import AbstractCache


class LocalInMemoryCache(AbstractCache):
    """Cache backed by an in-process LRU cache."""

    def __init__(self, maxsize: int = 1024) -> None:
        self._data: LRUCache = LRUCache(maxsize=maxsize)

    async def get(self, key: str) -> Any:
        return self._data.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)
