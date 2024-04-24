import pytest
from httpx import AsyncClient, ASGITransport

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
async def client(start_db) -> AsyncClient:

    transport = ASGITransport(
        app=app,
    )
    async with AsyncClient(
        # app=app,
        base_url="http://testserver/v1",
        headers={"Content-Type": "application/json"},
        transport=transport,
    ) as test_client:
        app.state.redis = await get_redis()
        yield test_client
