import logging

from fastapi import FastAPI

from the_app.api.nonsense import router as nonsense_router
from the_app.api.stuff import router as stuff_router
from the_app.database import engine
from the_app.models.base import Base

log = logging.getLogger(__name__)

app = FastAPI(title="Stuff And Nonsense", version="0.1")

app.include_router(stuff_router, prefix="/v1")
app.include_router(nonsense_router, prefix="/v1")


async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")
    await start_db()


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
