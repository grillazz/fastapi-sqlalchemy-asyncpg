from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from rotoger import AppStructLogger

from app.api.health import router as health_router
from app.api.ml import router as ml_router
from app.api.nonsense import router as nonsense_router
from app.api.shakespeare import router as shakespeare_router
from app.api.stuff import router as stuff_router
from app.api.user import router as user_router
from app.config import settings as global_settings
from app.exception_handlers import register_exception_handlers
from app.redis import get_redis
from app.services.auth import AuthBearer

logger = AppStructLogger().get_logger()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.redis = await get_redis()
    postgres_dsn = global_settings.postgres_url.unicode_string()
    try:
        app.postgres_pool = await asyncpg.create_pool(
            dsn=postgres_dsn,
            min_size=5,
            max_size=20,
        )
        await logger.ainfo(
            "Postgres pool created", idle_size=app.postgres_pool.get_idle_size()
        )
        yield
    except Exception as e:
        await logger.aerror("Error during app startup", error=repr(e))
        raise
    finally:
        await app.redis.close()
        await app.postgres_pool.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Stuff And Nonsense API",
        version="0.20.0",
        lifespan=lifespan,
    )
    app.include_router(stuff_router)
    app.include_router(nonsense_router)
    app.include_router(shakespeare_router)
    app.include_router(user_router)
    app.include_router(ml_router, prefix="/v1/ml", tags=["ML"])
    app.include_router(
        health_router, prefix="/v1/public/health", tags=["Health, Public"]
    )
    app.include_router(
        health_router,
        prefix="/v1/health",
        tags=["Health, Bearer"],
        dependencies=[Depends(AuthBearer())],
    )

    # Register exception handlers
    register_exception_handlers(app)

    @app.get("/index", response_class=HTMLResponse)
    def get_index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    return app


app = create_app()

# --- Unused/experimental code and TODOs ---
# from apscheduler import AsyncScheduler
# from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
# from apscheduler.eventbrokers.redis import RedisEventBroker
# from app.database import engine
# from app.services.scheduler import SchedulerMiddleware
# _scheduler_data_store = SQLAlchemyDataStore(engine, schema="scheduler")
# _scheduler_event_broker = RedisEventBroker(client_or_url=global_settings.redis_url.unicode_string())
# _scheduler_himself = AsyncScheduler(_scheduler_data_store, _scheduler_event_broker)
# app.add_middleware(SchedulerMiddleware, scheduler=_scheduler_himself)
# TODO: every non-GET method should reset cache
# TODO: scheduler tasks needing DB should access connection pool via request
# TODO: https://stackoverflow.com/questions/16053364/make-sure-only-one-worker-launches-the-apscheduler-event-in-a-pyramid-web-app-ru
