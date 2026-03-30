"""Database access layer for principal attributes."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db import DbSession
from app.exceptions import AttributeConflictError, DatabaseReadError, DatabaseWriteError
from app.models import PrincipalAttribute

logger = logging.getLogger(__name__)


async def get_principal_attributes_from_db(db: DbSession, principal_id: str) -> list[PrincipalAttribute]:
    """Return attributes for one principal from the database."""
    try:
        result = await db.execute(
            select(PrincipalAttribute).where(PrincipalAttribute.principal_id == principal_id)
        )
        return list(result.scalars().all())
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch attributes for principal_id=%s", principal_id)
        raise DatabaseReadError(f"Failed to fetch attributes for principal: {principal_id}") from exc


async def add_principal_attributes_to_db(
    db: DbSession, principal_id: str, attributes: dict[str, str], source_id: str = "entra_id",
) -> list[PrincipalAttribute]:
    """Create new attribute records from an external source. Returns created records."""
    now = datetime.now(timezone.utc)
    records = [
        PrincipalAttribute(
            principal_id=principal_id,
            attribute_key=key,
            attribute_value=value,
            source_id=source_id,
            last_updated_at=now,
        )
        for key, value in attributes.items()
    ]

    try:
        db.add_all(records)
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        logger.exception("Integrity error saving attributes for principal_id=%s", principal_id)
        raise AttributeConflictError(principal_id) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Failed to save attributes for principal_id=%s", principal_id)
        raise DatabaseWriteError(f"Failed to save attributes for principal: {principal_id}") from exc

    return records
