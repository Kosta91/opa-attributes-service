"""Tests for LocalInMemoryCache."""

import pytest

from app.cache.local_cache import LocalInMemoryCache


@pytest.mark.asyncio
async def test_get_set_delete():
    """Basic set → get → delete → get cycle."""
    cache = LocalInMemoryCache()

    assert await cache.get("key") is None

    await cache.set("key", {"foo": "bar"})
    assert await cache.get("key") == {"foo": "bar"}

    await cache.delete("key")
    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_overwrite():
    """Setting the same key overwrites the previous value."""
    cache = LocalInMemoryCache()

    await cache.set("key", "first")
    await cache.set("key", "second")
    assert await cache.get("key") == "second"


@pytest.mark.asyncio
async def test_delete_nonexistent():
    """Deleting a key that doesn't exist does not raise."""
    cache = LocalInMemoryCache()
    await cache.delete("nonexistent")
