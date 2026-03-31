"""Mock identity external attribute source for local development."""

from __future__ import annotations

from app.external.base import ExternalAttributeSource
from app.external.mock.mock_data import IDENTITY_ATTRIBUTES


class MockIdentitySource(ExternalAttributeSource):
    """Mock source returning identity attributes (email, name, oncall)."""

    @property
    def source_name(self) -> str:
        """Unique identifier for this source."""
        return "mock_identity"

    async def fetch_attributes(self, principal_id: str) -> dict[str, str] | None:
        """Return mock identity attributes for a principal."""
        return IDENTITY_ATTRIBUTES.get(principal_id)
