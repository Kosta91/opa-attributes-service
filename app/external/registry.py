"""External source registry and factory."""

from __future__ import annotations

import logging
from typing import Type

from app.crud import ensure_sources_exist
from app.db.base import AsyncSessionLocal
from app.external.base import ExternalAttributeSource
from app.external.entra_id import EntraIDAttributeSource
from app.external.mock.identity import MockIdentitySource
from app.external.mock.org import MockOrgSource
from app.external.settings import external_sources_settings

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, Type[ExternalAttributeSource]] = {
    "entra_id": EntraIDAttributeSource,
}

_MOCK_REGISTRY: dict[str, Type[ExternalAttributeSource]] = {
    "mock_identity": MockIdentitySource,
    "mock_org": MockOrgSource,
}


async def create_external_sources() -> list[ExternalAttributeSource]:
    """Instantiate external sources from settings and register missing ones in the DB.

    When ``MOCK_ENABLED`` is set, ignores ``EXTERNAL_SOURCES`` and creates
    mock sources instead.
    """
    if external_sources_settings.MOCK_ENABLED:
        registry = _MOCK_REGISTRY
        source_names = list(registry.keys())
        logger.info("Mock mode enabled — using mock external sources")
    else:
        registry = _REGISTRY
        source_names = external_sources_settings.EXTERNAL_SOURCES

    sources: list[ExternalAttributeSource] = []
    for name in source_names:
        cls = registry.get(name)
        if cls is None:
            raise ValueError(
                f"Unknown external source '{name}'. "
                f"Available: {sorted(registry.keys())}"
            )
        sources.append(cls())

    async with AsyncSessionLocal() as db:
        await ensure_sources_exist(db, source_names)

    logger.info("Initialised external sources: %s", source_names)
    return sources
