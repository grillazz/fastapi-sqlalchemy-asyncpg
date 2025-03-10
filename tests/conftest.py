from collections.abc import AsyncGenerator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import engine
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


@pytest.fixture(scope="session")
async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


@pytest.fixture(scope="session")
async def client(start_db) -> AsyncGenerator[AsyncClient, Any]:  # noqa: ARG001
    transport = ASGITransport(
        app=app,
    )
    async with AsyncClient(
        base_url="http://testserver/v1",
        headers={"Content-Type": "application/json"},
        transport=transport,
    ) as test_client:
        app.redis = await get_redis()
        yield test_client
