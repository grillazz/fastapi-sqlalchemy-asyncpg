import pytest
from httpx import AsyncClient
from the_app.main import app
from the_app.models.base import Base
from the_app.database import engine


@pytest.fixture(
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ]
)
def anyio_backend(request):
    return request.param


async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver/v1",
        headers={"Content-Type": "application/json"},
    ) as client:
        await start_db()
        yield client
        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()
