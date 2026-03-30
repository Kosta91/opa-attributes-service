from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.db import DbSession, get_db
from app.cache import InMemoryAttributeStore, get_store
from app.external import ExternalAttributeSource, get_external_source
from app.core import get_principal_attributes
from app.schemas import PrincipalAttributesResponse


router = APIRouter(prefix="/", tags=["OPA"])


@router.get(
    "/attributes/{principal_id}",
    response_model=PrincipalAttributesResponse,
    tags=["attributes"],
)
async def get_attributes(
    principal_id: str,
    db: DbSession = Depends(get_db),
    store: InMemoryAttributeStore = Depends(get_store),
    external: ExternalAttributeSource = Depends(get_external_source),
) -> PrincipalAttributesResponse:
    """Return aggregated attributes for one principal (email or other id)."""
    result = await get_principal_attributes(db, store, external, principal_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Principal not found")
    return result
