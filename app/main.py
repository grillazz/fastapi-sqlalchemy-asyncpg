import asyncpg
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.api.nonsense import router as nonsense_router
from app.api.shakespeare import router as shakespeare_router
from app.api.stuff import router as stuff_router
from app.config import settings as global_settings
from app.utils.logging import AppLogger
from app.api.user import router as user_router
from app.api.health import router as health_router
from app.redis import get_redis, get_cache
from app.services.auth import AuthBearer

logger = AppLogger().get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load the redis connection
    _app.redis = await get_redis()

    _postgres_dsn = global_settings.postgres_url.unicode_string()

    try:
        # Initialize the cache with the redis connection
        redis_cache = await get_cache()
        FastAPICache.init(RedisBackend(redis_cache), prefix="fastapi-cache")
        logger.info(FastAPICache.get_cache_status_header())
        # Initialize the postgres connection pool
        _app.postgres_pool = await asyncpg.create_pool(
            dsn=_postgres_dsn,
            min_size=5,
            max_size=20,
        )
        logger.info(f"Postgres pool created: {_app.postgres_pool.get_idle_size()=}")
        yield
    finally:
        # close redis connection and release the resources
        await _app.redis.close()
        # close postgres connection pool and release the resources
        await _app.postgres_pool.close()


app = FastAPI(title="Stuff And Nonsense API", version="0.15", lifespan=lifespan)

app.include_router(stuff_router)
app.include_router(nonsense_router)
app.include_router(shakespeare_router)
app.include_router(user_router)


app.include_router(health_router, prefix="/v1/public/health", tags=["Health, Public"])
app.include_router(
    health_router,
    prefix="/v1/health",
    tags=["Health, Bearer"],
    dependencies=[Depends(AuthBearer())],
)
