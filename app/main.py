from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from app.api.nonsense import router as nonsense_router
from app.api.shakespeare import router as shakespeare_router
from app.api.stuff import router as stuff_router
from app.utils.logging import AppLogger
from app.api.user import router as user_router
from app.api.health import router as health_router
from app.redis import get_redis
from app.services.auth import AuthBearer

logger = AppLogger().get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the redis connection
    app.state.redis = await get_redis()
    try:
        yield
    finally:
        # close redis connection and release the resources
        app.state.redis.close()


app = FastAPI(title="Stuff And Nonsense API", version="0.6", lifespan=lifespan)

app.include_router(stuff_router)
app.include_router(nonsense_router)
app.include_router(shakespeare_router)
app.include_router(user_router)


app.include_router(health_router, prefix="/v1/public/health", tags=["Health, Public"])
app.include_router(health_router, prefix="/v1/health", tags=["Health, Bearer"], dependencies=[Depends(AuthBearer())])
