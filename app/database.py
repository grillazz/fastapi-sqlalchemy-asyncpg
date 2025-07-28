from collections.abc import AsyncGenerator

from rotoger import AppStructLogger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings as global_settings

logger = AppStructLogger().get_logger()

engine = create_async_engine(
    global_settings.asyncpg_url.unicode_string(),
    future=True,
    echo=True,
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)


# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        try:
            yield session
        except Exception as e:
            await logger.aerror(f"Error getting database session: {e}")
            raise
