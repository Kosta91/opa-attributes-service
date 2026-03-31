"""Tests for mock external attribute sources."""

import pytest

from app.external.mock.identity import MockIdentitySource
from app.external.mock.org import MockOrgSource


@pytest.mark.asyncio
async def test_mock_identity_known_principal():
    """MockIdentitySource returns identity attributes for known principals."""
    source = MockIdentitySource()
    attrs = await source.fetch_attributes("alice")

    assert attrs is not None
    assert attrs["email"] == "alice@example.com"
    assert attrs["name"] == "Alice Johnson"
    assert "oncall" in attrs


@pytest.mark.asyncio
async def test_mock_identity_unknown_principal():
    """MockIdentitySource returns None for unknown principals."""
    source = MockIdentitySource()
    assert await source.fetch_attributes("nonexistent") is None


@pytest.mark.asyncio
async def test_mock_org_known_principal():
    """MockOrgSource returns org attributes for known principals."""
    source = MockOrgSource()
    attrs = await source.fetch_attributes("bob")

    assert attrs is not None
    assert attrs["department"] == "ProdSec"
    assert attrs["jobTitle"] == "Staff Security Engineer"
    assert "team" in attrs
    assert "location" in attrs


@pytest.mark.asyncio
async def test_mock_org_unknown_principal():
    """MockOrgSource returns None for unknown principals."""
    source = MockOrgSource()
    assert await source.fetch_attributes("nonexistent") is None


@pytest.mark.asyncio
async def test_source_name_property():
    """Each mock source exposes the correct source_name."""
    assert MockIdentitySource().source_name == "mock_identity"
    assert MockOrgSource().source_name == "mock_org"
