from asyncio import current_task

from typing import AsyncGenerator

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session
from sqlalchemy.orm import sessionmaker

from app import config

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
async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
AsyncScopedSession = async_scoped_session(async_session_factory, scopefunc=current_task)


# Dependency
async def get_db() -> AsyncGenerator:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as sql_ex:
            await session.rollback()
            raise sql_ex
        except HTTPException as http_ex:
            await session.rollback()
            raise http_ex
        finally:
            await session.close()

