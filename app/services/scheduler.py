from datetime import datetime

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from attrs import define
from sqlalchemy import text
from starlette.types import ASGIApp, Receive, Scope, Send

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


@define
class SchedulerMiddleware:
    app: ASGIApp
    scheduler: AsyncScheduler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles the incoming request and schedules tasks if the scope type is 'lifespan'.

        Args:
            scope (Scope): The ASGI scope dictionary containing request information.
            receive (Receive): The ASGI receive callable.
            send (Send): The ASGI send callable.
        """
        if scope["type"] == "lifespan":
            async with self.scheduler:
                await self.scheduler.add_schedule(
                    tick, IntervalTrigger(seconds=25), id="tick-sql-25"
                )
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
