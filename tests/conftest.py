"""Shared test fixtures."""

from __future__ import annotations

from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.cache.local_cache import LocalInMemoryCache
from app.db.base import Base
from app.external.mock.identity import MockIdentitySource
from app.external.mock.org import MockOrgSource

import app.models  # noqa: register ORM models in Base.metadata


# ---------------------------------------------------------------------------
# Database — async SQLite in-memory
# ---------------------------------------------------------------------------

_test_engine = create_async_engine("sqlite+aiosqlite://", echo=False)
_TestSessionLocal = async_sessionmaker(bind=_test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db():
    """Yield a clean async DB session backed by in-memory SQLite."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _TestSessionLocal() as session:
        yield session

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_cache():
    """Return a fresh in-memory cache."""
    return LocalInMemoryCache()


# ---------------------------------------------------------------------------
# External sources
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_externals():
    """Return a list of mock external attribute sources."""
    return [MockIdentitySource(), MockOrgSource()]


# ---------------------------------------------------------------------------
# FastAPI TestClient
# ---------------------------------------------------------------------------

@pytest.fixture
def app_client(db, mock_cache, mock_externals):
    """Return a TestClient with overridden dependencies and a no-op lifespan."""
    from app.api import public_router, register_exception_handlers
    from app.db import get_db
    from app.cache.base import get_cache
    from app.external.base import get_external_sources

    @asynccontextmanager
    async def _test_lifespan(application: FastAPI):
        yield

    test_app = FastAPI(lifespan=_test_lifespan)
    register_exception_handlers(test_app)
    test_app.include_router(public_router)

    # Wire /health, /ready, / from the real app
    from app.app import health, root
    test_app.get("/health", tags=["health"])(health)
    test_app.get("/", tags=["root"])(root)

    async def _override_db():
        yield db

    test_app.dependency_overrides[get_db] = _override_db
    test_app.dependency_overrides[get_cache] = lambda: mock_cache
    test_app.dependency_overrides[get_external_sources] = lambda: mock_externals

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield client
