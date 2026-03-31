"""CRUD operations for principal attributes."""

from app.crud.opa import get_principal_attributes_from_db, add_principal_attributes_to_db
from app.crud.sync import (
    ensure_sources_exist,
    get_principal_ids_by_source,
    get_principal_attributes_by_source,
    upsert_principal_attributes,
    delete_principal_attributes_by_source,
    update_source_sync_status,
)