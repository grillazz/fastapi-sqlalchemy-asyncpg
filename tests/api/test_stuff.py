import pytest
from fastapi import status
from httpx import AsyncClient

# decorate all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


async def test_add_stuff(client: AsyncClient):
    assert True
