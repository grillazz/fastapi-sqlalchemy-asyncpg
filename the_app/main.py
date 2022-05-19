from fastapi import FastAPI

from the_app.api.nonsense import router as nonsense_router
from the_app.api.stuff import router as stuff_router
from the_app.api.upload_csv import router as upload_router
from the_app.database import engine
from the_app.models.base import Base
from the_app.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Stuff And Nonsense API", version="0.3")

app.include_router(stuff_router)
app.include_router(nonsense_router)
app.include_router(upload_router)


async def start_db():
    async with engine.begin() as conn:
        print("database connection start")
        # await conn.run_sync(Base.metadata.create_all)
    # await engine.dispose()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await start_db()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
