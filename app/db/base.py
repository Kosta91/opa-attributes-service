"""SQLAlchemy async engine, session factory, and declarative base."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncIterator

from app.db.db_settings import db_settings

Base = declarative_base()

DATABASE_URL = db_settings.DATABASE_URL

# Type alias for the database session
DbSession = AsyncSession

# Enable SQL echo only if DEBUG_SQL env var is set
_echo_sql = db_settings.DEBUG_SQL

engine = create_async_engine(
    db_settings.DATABASE_URL,
    echo=_echo_sql,  # Controlled by DEBUG_SQL env var
    future=True,
    pool_size=db_settings.DB_POOL_SIZE,
    max_overflow=db_settings.DB_MAX_OVERFLOW,
    pool_timeout=db_settings.DB_POOL_TIMEOUT,
    pool_recycle=db_settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
)

AsyncSessionLocal: async_sessionmaker[DbSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
        
async def create_tables() -> None:
    """Create all tables if they don't exist yet."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncIterator[DbSession]:
    """Yield a database session.

    Use as a FastAPI dependency: ``Depends(get_db)``.
    For standalone context-manager usage, use :func:`get_db_ctx`.
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()