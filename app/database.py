from collections.abc import AsyncGenerator

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import config
from app.utils import get_logger

logger = get_logger(__name__)

global_settings = config.get_settings()
url = global_settings.asyncpg_url

engine = create_async_engine(
    url,
    future=True,
    echo=True,
    json_serializer=jsonable_encoder,
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = sessionmaker(
    engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session
