from contextlib import asynccontextmanager

import asyncpg
from apscheduler import AsyncScheduler
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.redis import RedisEventBroker
from fastapi import Depends, FastAPI

from app.api.health import router as health_router
from app.api.nonsense import router as nonsense_router
from app.api.shakespeare import router as shakespeare_router
from app.api.stuff import router as stuff_router
from app.api.user import router as user_router
from app.api.ml import router as ml_router
from app.config import settings as global_settings
from app.database import engine
from app.redis import get_redis
from app.services.auth import AuthBearer
from app.services.scheduler import SchedulerMiddleware
from app.utils.logging import AppLogger

logger = AppLogger().get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load the redis connection
    _app.redis = await get_redis()

    _postgres_dsn = global_settings.postgres_url.unicode_string()

    try:
        # TODO: cache with the redis connection
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


app = FastAPI(title="Stuff And Nonsense API", version="0.18.0", lifespan=lifespan)

app.include_router(stuff_router)
app.include_router(nonsense_router)
app.include_router(shakespeare_router)
app.include_router(user_router)
app.include_router(ml_router, prefix="/v1/ml", tags=["ML"])


app.include_router(health_router, prefix="/v1/public/health", tags=["Health, Public"])
app.include_router(
    health_router,
    prefix="/v1/health",
    tags=["Health, Bearer"],
    dependencies=[Depends(AuthBearer())],
)

_scheduler_data_store = SQLAlchemyDataStore(engine, schema="scheduler")
_scheduler_event_broker = RedisEventBroker(
    client_or_url=global_settings.redis_url.unicode_string()
)
_scheduler_himself = AsyncScheduler(_scheduler_data_store, _scheduler_event_broker)

app.add_middleware(SchedulerMiddleware, scheduler=_scheduler_himself)


# TODO: every not GET meth should reset cache
# TODO: every scheduler task which needs to act on database should have access to connection pool via request - maybe ?
# TODO: https://stackoverflow.com/questions/16053364/make-sure-only-one-worker-launches-the-apscheduler-event-in-a-pyramid-web-app-ru
