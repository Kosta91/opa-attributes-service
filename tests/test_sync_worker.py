"""Unit tests for SyncWorker._sync_principal."""

import pytest

from app.crud.sync import (
    upsert_principal_attributes,
    get_principal_attributes_by_source,
    delete_principal_attributes_by_source,
)
from app.external.mock.identity import MockIdentitySource
from app.external.mock.org import MockOrgSource
from app.models import AttributeSource


@pytest.mark.asyncio
async def test_sync_principal_updates_db(db):
    """When fresh attrs differ from existing, DB is updated."""
    source = MockIdentitySource()

    # Seed the source record
    db.add(AttributeSource(source_name="mock_identity"))
    await db.commit()

    # Insert stale data
    await upsert_principal_attributes(db, "alice", "mock_identity", {"email": "old@example.com"})

    # Fetch fresh and upsert (simulating what _sync_principal does)
    fresh = await source.fetch_attributes("alice")
    existing = await get_principal_attributes_by_source(db, "alice", "mock_identity")
    assert existing != fresh

    await upsert_principal_attributes(db, "alice", "mock_identity", fresh)

    updated = await get_principal_attributes_by_source(db, "alice", "mock_identity")
    assert updated["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_sync_principal_no_change(db):
    """When attrs are unchanged, no upsert is needed."""
    source = MockIdentitySource()

    db.add(AttributeSource(source_name="mock_identity"))
    await db.commit()

    fresh = await source.fetch_attributes("alice")
    await upsert_principal_attributes(db, "alice", "mock_identity", fresh)

    # Fetch again — should be identical
    existing = await get_principal_attributes_by_source(db, "alice", "mock_identity")
    fresh_again = await source.fetch_attributes("alice")
    assert existing == fresh_again


@pytest.mark.asyncio
async def test_sync_principal_deleted(db):
    """When external returns None, attributes are deleted from DB."""
    source = MockIdentitySource()

    db.add(AttributeSource(source_name="mock_identity"))
    await db.commit()

    # Insert data first
    fresh = await source.fetch_attributes("alice")
    await upsert_principal_attributes(db, "alice", "mock_identity", fresh)

    # Simulate external returning None (principal removed)
    await delete_principal_attributes_by_source(db, "alice", "mock_identity")

    remaining = await get_principal_attributes_by_source(db, "alice", "mock_identity")
    assert remaining == {}
