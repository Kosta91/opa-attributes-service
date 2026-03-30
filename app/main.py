from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI

from app.cache import RedisAttributeStore, LocalAttributeStore
from app.external import EntraIDAttributeSource
from app.redis import get_redis, get_redis_pool
from app.redis.redis import Redis
from app.redis.redis_settings import redis_settings

import uvicorn


@asynccontextmanager
async def lifespan(application: FastAPI):
    if redis_settings.REDIS_ENABLED:
        application.state.store = RedisAttributeStore(get_redis_pool())
    else:
        application.state.store = LocalAttributeStore()
    application.state.external_source = EntraIDAttributeSource()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health", tags=["health"])
async def health(redis: Redis | None = Depends(get_redis)) -> dict[str, str]:
    """Health-check endpoint."""
    if redis is not None:
        try:
            await redis.ping()
        except Exception:
            return {"status": "degraded", "redis": "unavailable"}
    return {"status": "ok"}


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Root route with a short service identifier."""
    return {"service": "prodsec.opa_attribute_storage"}


if __name__ == "__main__":
    uvicorn.run(app)
