"""Public API endpoints for OPA attribute lookups."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.auth import require_auth
from app.db import DbSession, get_db
from app.cache import AbstractCache, get_cache
from app.external import ExternalAttributeSource, get_external_sources
from app.core import get_principal_attributes
from app.schemas import PrincipalAttributesResponse


router = APIRouter(
    prefix="",
    tags=["OPA"],
    dependencies=[Depends(require_auth)],
)


@router.get(
    "/attributes/{principal_id}",
    response_model=PrincipalAttributesResponse,
    tags=["attributes"],
)
async def get_attributes(
    principal_id: str,
    db: DbSession = Depends(get_db),
    store: AbstractCache = Depends(get_cache),
    externals: list[ExternalAttributeSource] = Depends(get_external_sources),
) -> PrincipalAttributesResponse:
    """Return aggregated attributes for one principal (email or other id)."""
    return await get_principal_attributes(db, store, externals, principal_id)
