"""Attribute resolution pipeline: cache -> database -> external sources."""

from __future__ import annotations

import logging

from app.cache.base import AbstractCache
from app.crud import get_principal_attributes_from_db, add_principal_attributes_to_db
from app.db import DbSession
from app.exceptions import PrincipalNotFoundError
from app.external.base import ExternalAttributeSource
from app.models import PrincipalAttribute
from app.cache.keys import principal_attrs_key
from app.schemas import PrincipalAttributesResponse

from typing import Dict, List


logger = logging.getLogger(__name__)


async def get_principal_attributes(
    db: DbSession,
    cache: AbstractCache,
    externals: list[ExternalAttributeSource],
    principal_id: str,
) -> PrincipalAttributesResponse:
    """Return aggregated attributes for one principal (email or other id)."""
    cache_key = principal_attrs_key(principal_id)

    # 1. In-memory cache
    try:
        cached = await cache.get(cache_key)
        if cached is not None:
            return PrincipalAttributesResponse(
                principal_id=principal_id,
                attributes=cached,
            )
    except Exception:
        logger.exception("Cache read failed for key=%s, falling through to DB", cache_key)

    # 2. Database
    db_attrs: List[PrincipalAttribute] = await get_principal_attributes_from_db(db, principal_id)
    if db_attrs:
        attrs_dict = {a.attribute_key: a.attribute_value for a in db_attrs}
        await __add_attrs_to_store(cache, cache_key, attrs_dict)
        return PrincipalAttributesResponse(
            principal_id=principal_id,
            attributes=attrs_dict,
        )

    # 3. External sources — query each separately, persist per source
    for source in externals:
        try:
            attrs = await source.fetch_attributes(principal_id)
        except Exception:
            logger.exception("External source %s failed for principal=%s", source.source_name, principal_id)
            continue
        if attrs:
            await add_principal_attributes_to_db(db, principal_id, attrs, source_name=source.source_name)

    # Re-read from DB to get the full picture across all sources
    db_attrs = await get_principal_attributes_from_db(db, principal_id)
    if not db_attrs:
        raise PrincipalNotFoundError(principal_id)

    attrs_dict = {a.attribute_key: a.attribute_value for a in db_attrs}
    await __add_attrs_to_store(cache, cache_key, attrs_dict)

    return PrincipalAttributesResponse(
        principal_id=principal_id,
        attributes=attrs_dict,
    )
    

async def __add_attrs_to_store(
    cache: AbstractCache, 
    cache_key: str, 
    attributes: Dict[str, str]
) -> None:
    """Helper to add attributes to cache, with error handling."""
    try:
        await cache.set(cache_key, attributes)
    except Exception:
        logger.exception("Cache write failed for key=%s", cache_key)
