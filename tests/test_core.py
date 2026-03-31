"""Unit tests for the attribute resolution pipeline (app.core.opa)."""

import pytest
import pytest_asyncio

from app.cache.local_cache import LocalInMemoryCache
from app.cache.keys import principal_attrs_key
from app.core.opa import get_principal_attributes
from app.exceptions import PrincipalNotFoundError
from app.external.mock.identity import MockIdentitySource
from app.external.mock.org import MockOrgSource


@pytest.mark.asyncio
async def test_returns_from_cache(db, mock_cache):
    """When attributes are cached, return them without hitting DB or externals."""
    cached = {"email": "cached@example.com"}
    await mock_cache.set(principal_attrs_key("alice"), cached)

    result = await get_principal_attributes(db, mock_cache, [], "alice")

    assert result.principal_id == "alice"
    assert result.attributes == cached


@pytest.mark.asyncio
async def test_returns_from_db(db, mock_cache, mock_externals):
    """When cache is empty but DB has data, return from DB and populate cache."""
    # First call populates DB from externals
    await get_principal_attributes(db, mock_cache, mock_externals, "bob")

    # Clear cache
    await mock_cache.delete(principal_attrs_key("bob"))

    # Second call should read from DB (no externals needed)
    result = await get_principal_attributes(db, mock_cache, [], "bob")

    assert result.principal_id == "bob"
    assert "email" in result.attributes


@pytest.mark.asyncio
async def test_fetches_from_externals(db, mock_cache, mock_externals):
    """When cache and DB are empty, fetch from external sources."""
    result = await get_principal_attributes(db, mock_cache, mock_externals, "alice")

    assert result.principal_id == "alice"
    assert result.attributes["email"] == "alice@example.com"
    assert result.attributes["department"] == "Vehicle Security"

    # Verify it was cached
    cached = await mock_cache.get(principal_attrs_key("alice"))
    assert cached is not None
    assert cached["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_raises_not_found(db, mock_cache):
    """When principal is not found anywhere, raise PrincipalNotFoundError."""
    with pytest.raises(PrincipalNotFoundError):
        await get_principal_attributes(db, mock_cache, [MockIdentitySource()], "nonexistent")
