from __future__ import annotations


from cachetools import LRUCache
from typing import Any

from app.cache.base import InMemoryAttributeStore


class LocalAttributeStore(InMemoryAttributeStore):
    """Cache backed by an in-process LRU cache."""

    def __init__(self, maxsize: int = 1024) -> None:
        self._data: LRUCache = LRUCache(maxsize=maxsize)

    async def get(self, key: str) -> Any | None:
        return self._data.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._data[key] = value
