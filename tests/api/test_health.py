import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_redis_health(client: AsyncClient):
    response = await client.get("/public/health/redis")
    assert response.status_code == status.HTTP_200_OK
    # assert payload["name"] == response.json()["name"]
    # assert UUID(response.json()["id"])
