from datetime import datetime

from starlette.types import ASGIApp, Receive, Scope, Send

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.utils.logging import AppLogger

logger = AppLogger().get_logger()


def tick():

    logger.info(f">>>> Be or not to be...{datetime.now()}")


class SchedulerMiddleware:
    # TODO: need access to request to be able to get db conn pool

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
                    tick, IntervalTrigger(seconds=25), id="tick"
                )
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
