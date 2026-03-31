"""Abstract interface for external attribute sources and FastAPI dependency."""

from __future__ import annotations

from abc import ABC, abstractmethod

from fastapi import Request


class ExternalAttributeSource(ABC):
    """Abstract interface for fetching attributes from an external source."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this source (must match attribute_sources.id in the DB)."""

    @abstractmethod
    async def fetch_attributes(self, principal_id: str) -> dict[str, str] | None:
        """Fetch attributes for a principal. Returns None if not found."""


def get_external_sources(request: Request) -> list[ExternalAttributeSource]:
    """FastAPI dependency — returns external sources registered during lifespan."""
    return request.app.state.external_sources
