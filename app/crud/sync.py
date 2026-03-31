"""CRUD operations for background sync of principal attributes."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select, update, delete

from app.db import DbSession
from app.models import AttributeSource, PrincipalAttribute

logger = logging.getLogger("sync.crud")


async def get_all_sources(db: DbSession) -> list[AttributeSource]:
    """Return all registered attribute sources."""
    result = await db.execute(select(AttributeSource))
    return list(result.scalars().all())


async def ensure_sources_exist(
    db: DbSession, 
    source_names: list[str]
) -> None:
    """Insert missing attribute sources into the DB. Existing ones are left unchanged."""
    result = await db.execute(
        select(AttributeSource.source_name).where(
            AttributeSource.source_name.in_(source_names)
        )
    )
    existing = set(result.scalars().all())
    missing = [name for name in source_names if name not in existing]

    if not missing:
        return

    for name in missing:
        db.add(AttributeSource(source_name=name))
        logger.info("Registered new attribute source: %s", name)

    await db.commit()


async def get_principal_ids_by_source(
    db: DbSession, 
    source_name: str
) -> list[str]:
    """Return distinct principal IDs that have attributes from the given source."""
    result = await db.execute(
        select(PrincipalAttribute.principal_id)
        .where(PrincipalAttribute.source_name == source_name)
        .distinct()
    )
    return list(result.scalars().all())


async def get_principal_attributes_by_source(
    db: DbSession, 
    principal_id: str, source_name: str,
) -> dict[str, str]:
    """Return existing attributes for a principal from a specific source as a dict."""
    result = await db.execute(
        select(PrincipalAttribute).where(
            PrincipalAttribute.principal_id == principal_id,
            PrincipalAttribute.source_name == source_name,
        )
    )
    return {r.attribute_key: r.attribute_value for r in result.scalars().all()}


async def upsert_principal_attributes(
    db: DbSession,
    principal_id: str,
    source_name: str,
    attributes: dict[str, str],
) -> None:
    """Replace all attributes for a principal from a given source with fresh data."""
    now = datetime.now(timezone.utc)

    await db.execute(
        delete(PrincipalAttribute).where(
            PrincipalAttribute.principal_id == principal_id,
            PrincipalAttribute.source_name == source_name,
        )
    )

    records = [
        PrincipalAttribute(
            principal_id=principal_id,
            attribute_key=key,
            attribute_value=value,
            source_name=source_name,
            last_updated_at=now,
        )
        for key, value in attributes.items()
    ]
    db.add_all(records)
    await db.commit()


async def delete_principal_attributes_by_source(
    db: DbSession, 
    principal_id: str, 
    source_name: str,
) -> None:
    """Delete all attributes for a principal from a given source."""
    await db.execute(
        delete(PrincipalAttribute).where(
            PrincipalAttribute.principal_id == principal_id,
            PrincipalAttribute.source_name == source_name,
        )
    )
    await db.commit()


async def update_source_sync_status(
    db: DbSession, 
    source_name: str, status: str,
) -> None:
    """Update sync_status and last_sync timestamp for an attribute source."""
    await db.execute(
        update(AttributeSource)
        .where(AttributeSource.id == source_name)
        .values(sync_status=status, last_sync=datetime.now(timezone.utc))
    )
    await db.commit()
