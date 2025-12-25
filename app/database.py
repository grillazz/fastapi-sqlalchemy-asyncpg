from collections.abc import AsyncGenerator

from fastapi.exceptions import ResponseValidationError
from rotoger import get_logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings as global_settings

logger = get_logger()

engine = create_async_engine(
    global_settings.asyncpg_url.unicode_string(),
    future=True,
    echo=True,
)

test_engine = create_async_engine(
    global_settings.test_asyncpg_url.unicode_string(),
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

TestAsyncSessionFactory = async_sessionmaker(
    test_engine,
    autoflush=False,
    expire_on_commit=False,
)


# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            # Re-raise SQLAlchemy errors to be handled by the global handler
            raise
        except Exception as ex:
            # Only log actual database-related issues, not response validation
            if not isinstance(ex, ResponseValidationError):
                await logger.aerror(f"Database-related error: {repr(ex)}")
            raise  # Re-raise to be handled by appropriate handlers


async def get_test_db() -> AsyncGenerator:
    async with TestAsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            # Re-raise SQLAlchemy errors to be handled by the global handler
            raise
        except Exception as ex:
            # Only log actual database-related issues, not response validation
            if not isinstance(ex, ResponseValidationError):
                await logger.aerror(f"Database-related error: {repr(ex)}")
            raise  # Re-raise to be handled by appropriate handlers