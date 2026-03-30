"""OPA Attributes Service — FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from typing import Dict, Optional

from sqlalchemy import text

from app.api import public_router, register_exception_handlers
from app.cache import RedisAttributeStore, LocalAttributeStore
from app.db import DbSession, get_db
from app.external import EntraIDAttributeSource
from app.redis import get_redis, get_redis_pool
from app.redis.redis import Redis
from app.redis.redis_settings import redis_settings
from app.sync import SyncWorker

import uvicorn


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize application-wide dependencies (cache store, external source)."""
    if redis_settings.REDIS_ENABLED:
        application.state.store = RedisAttributeStore(get_redis_pool())
    else:
        application.state.store = LocalAttributeStore()
    application.state.external_source = EntraIDAttributeSource()

    sync_worker = SyncWorker(
        store=application.state.store,
        external=application.state.external_source,
    )
    sync_worker.start()

    yield

    await sync_worker.stop()


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)
app.include_router(public_router)


@app.get("/ready", tags=["health"])
async def readiness(
    db: DbSession = Depends(get_db),
    redis: Optional[Redis] = Depends(get_redis),
) -> Dict[str, str]:
    """Readiness probe — checks that all dependencies are reachable."""
    checks: Dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"

    if redis is not None:
        try:
            await redis.ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "unavailable"

    status = "ok" if all(v == "ok" for v in checks.values()) else "unavailable"
    return {"status": status, **checks}


@app.get("/health", tags=["health"])
async def health(redis: Optional[Redis] = Depends(get_redis)) -> Dict[str, str]:
    """Health-check endpoint."""
    if redis is not None:
        try:
            await redis.ping()
        except Exception:
            return {"status": "degraded", "redis": "unavailable"}
    return {"status": "ok"}


@app.get("/", tags=["root"])
def root() -> Dict[str, str]:
    """Root route with a short service identifier."""
    return {"service": "prodsec.opa_attribute_storage"}


if __name__ == "__main__":
    uvicorn.run(app)
