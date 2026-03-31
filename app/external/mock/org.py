"""Mock org external attribute source for local development."""

from __future__ import annotations

from app.external.base import ExternalAttributeSource
from app.external.mock.mock_data import ORG_ATTRIBUTES


class MockOrgSource(ExternalAttributeSource):
    """Mock source returning org attributes (department, jobTitle, team, location)."""

    @property
    def source_name(self) -> str:
        """Unique identifier for this source."""
        return "mock_org"

    async def fetch_attributes(self, principal_id: str) -> dict[str, str] | None:
        """Return mock org attributes for a principal."""
        return ORG_ATTRIBUTES.get(principal_id)
