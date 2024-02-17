from anyio import Path

import pytest
from fastapi import status
from httpx import AsyncClient

# Integration tests
pytestmark = pytest.mark.anyio


async def test_import_animals(client: AsyncClient):
    # Arrange
    expected_status = status.HTTP_201_CREATED
    headers = {"Content-type": "multipart/form-data; boundary={}"}

    path = Path("tests/api/nonsense.xlsx")

    _bytes = await path.read_bytes()

    response = await client.post(
        "/nonsense/import",
        files={"xlsx": ("nonsense.xlsx", _bytes)},
        headers=headers,
    )

    assert response.status_code == expected_status
    assert response.json() == {'filename': 'nonsense.xlsx', 'nonsense_records': 10}
