from fastapi import FastAPI

from the_app.api.nonsense import router as nonsense_router
from the_app.api.stuff import router as stuff_router
from the_app.api.shakespeare import router as shakespeare_router
from the_app.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Stuff And Nonsense API", version="0.4")

app.include_router(stuff_router)
app.include_router(nonsense_router)
app.include_router(shakespeare_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
