"""External source registry and factory."""

from __future__ import annotations

import logging
from typing import Type

from app.crud import ensure_sources_exist
from app.db.base import AsyncSessionLocal
from app.external.base import ExternalAttributeSource
from app.external.entra_id import EntraIDAttributeSource
from app.external.settings import external_sources_settings

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, Type[ExternalAttributeSource]] = {
    "entra_id": EntraIDAttributeSource,
}


async def create_external_sources() -> list[ExternalAttributeSource]:
    """Instantiate external sources from settings and register missing ones in the DB.

    Reads ``EXTERNAL_SOURCES`` from environment, creates instances via the
    registry, and ensures every source name has a corresponding row in the
    ``attribute_sources`` table.
    """
    source_names = external_sources_settings.EXTERNAL_SOURCES

    sources: list[ExternalAttributeSource] = []
    for name in source_names:
        cls = _REGISTRY.get(name)
        if cls is None:
            raise ValueError(
                f"Unknown external source '{name}'. "
                f"Available: {sorted(_REGISTRY.keys())}"
            )
        sources.append(cls())

    async with AsyncSessionLocal() as db:
        await ensure_sources_exist(db, source_names)

    logger.info("Initialised external sources: %s", source_names)
    return sources
