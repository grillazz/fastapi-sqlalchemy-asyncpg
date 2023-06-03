from fastapi import FastAPI

from app.api.nonsense import router as nonsense_router
from app.api.shakespeare import router as shakespeare_router
from app.api.stuff import router as stuff_router
from app.utils.logging import AppLogger

logger = AppLogger.__call__().get_logger()

app = FastAPI(title="Stuff And Nonsense API", version="0.5")

app.include_router(stuff_router)
app.include_router(nonsense_router)
app.include_router(shakespeare_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
