"""Abstract interface for external attribute sources and FastAPI dependency."""

from __future__ import annotations

from abc import ABC, abstractmethod

from fastapi import Request


class ExternalAttributeSource(ABC):
    """Abstract interface for fetching attributes from an external source."""

    @abstractmethod
    async def fetch_attributes(self, principal_id: str) -> dict[str, str] | None:
        """Fetch attributes for a principal. Returns None if not found."""


def get_external_source(request: Request) -> ExternalAttributeSource:
    """FastAPI dependency — returns the external source created during lifespan."""
    return request.app.state.external_source
