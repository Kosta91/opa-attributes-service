from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from fastapi import Request


class InMemoryAttributeStore(ABC):
    """Abstract cache interface for attribute storage."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return cached value or None on miss."""

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """Store a value."""


def get_store(request: Request) -> InMemoryAttributeStore:
    """FastAPI dependency — returns the store created during lifespan."""
    return request.app.state.store
