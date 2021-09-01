from fastapi import FastAPI

from the_app.api.nonsense import router as nonsense_router
from the_app.api.stuff import router as stuff_router
from the_app.database import engine
from the_app.models.base import Base
from the_app.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Stuff And Nonsense", version="0.2")

app.include_router(stuff_router)
app.include_router(nonsense_router)


async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await start_db()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
