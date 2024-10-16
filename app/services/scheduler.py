from datetime import datetime

from sqlalchemy import text
from starlette.types import ASGIApp, Receive, Scope, Send
from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import AsyncSessionFactory
from app.utils.logging import AppLogger

logger = AppLogger().get_logger()


async def tick():
    async with AsyncSessionFactory() as session:
        stmt = text("select 1;")
        logger.info(f">>>> Be or not to be...{datetime.now()}")
        result = await session.execute(stmt)
        logger.info(f">>>> Result: {result.scalar()}")
        return True


class SchedulerMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        scheduler: AsyncScheduler,
    ) -> None:
        self.app = app
        self.scheduler = scheduler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            async with self.scheduler:
                await self.scheduler.add_schedule(
                    tick, IntervalTrigger(seconds=25), id="tick-sql-25"
                )
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
