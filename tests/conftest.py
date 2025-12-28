from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, get_db, test_engine
from app.main import app
from app.models.base import Base
from app.redis import get_redis


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ],
)
def anyio_backend(request):
    return request.param


def _create_db(conn) -> None:
    """Create the test database if it doesn't exist."""
    try:
        conn.execute(text("CREATE DATABASE testdb"))
    except ProgrammingError:
        # This might be raised by databases that don't support `IF NOT EXISTS`
        # and the schema already exists. You can choose to ignore it.
        pass


def _create_db_schema(conn) -> None:
    """Create a database schema if it doesn't exist."""
    try:
        """Create a database schema if it doesn't exist."""
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS happy_hog"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS shakespeare"))
    except ProgrammingError:
        # This might be raised by databases that don't support `IF NOT EXISTS`
        # and the schema already exists. You can choose to ignore it.
        pass


@pytest.fixture(scope="session")
async def start_db():
    # The `engine` is configured for the default 'postgres' database.
    # We connect to it and create the test database.
    # A transaction block is not used, as CREATE DATABASE cannot run inside it.
    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))  # Ensure we're not in a transaction
        await conn.run_sync(_create_db)

    # Now, connect to the newly created `testdb` with `test_engine`
    async with test_engine.begin() as conn:
        await conn.run_sync(_create_db_schema)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    Provide a transactional database session for each test function.
    Rolls back changes after the test.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, Any]:
    """
    Provide a test client for making API requests.
    Uses the function-scoped db_session for test isolation.
    """

    def get_test_db_override():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db_override
    app.redis = await get_redis()

    transport = ASGITransport(app=app)
    async with AsyncClient(
        base_url="http://testserver/v1",
        headers={"Content-Type": "application/json"},
        transport=transport,
    ) as test_client:
        yield test_client

    # Clean up dependency overrides
    del app.dependency_overrides[get_db]
