import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from the_app.main import app
from the_app import config
from the_app.database import get_db, engine
from the_app.models.base import Base

global_settings = config.get_settings()
url = global_settings.asyncpg_test_url
engine = create_async_engine(url)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_test_db():
    session = async_session()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as ex:
        await session.rollback()
        raise ex
    finally:
        await session.close()

app.dependency_overrides[get_db] = get_test_db


async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        await start_db()
        yield client
