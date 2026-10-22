from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler import AsyncScheduler, ConflictPolicy
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.redis import RedisEventBroker
from apscheduler.triggers.interval import IntervalTrigger
from rotoger import get_logger
from sqlalchemy import text

from app.config import settings as global_settings
from app.database import AsyncSessionFactory, engine

logger = get_logger()


async def tick():
    async with AsyncSessionFactory() as session:
        stmt = text("select 1;")
        await logger.ainfo(f">>>> Be or not to be...{datetime.now()}")
        result = await session.execute(stmt)
        await logger.ainfo(f">>>> Result: {result.scalar()}")
        return True


@asynccontextmanager
async def scheduler_lifespan() -> AsyncIterator[None]:
    scheduler = AsyncScheduler(
        SQLAlchemyDataStore(engine, schema="scheduler"),
        RedisEventBroker(client_or_url=global_settings.redis_url.unicode_string()),
    )

    async with scheduler:
        await scheduler.add_schedule(
            tick,
            IntervalTrigger(seconds=25),
            id="tick-sql-25",
            conflict_policy=ConflictPolicy.replace,
        )
        await scheduler.start_in_background()
        yield
