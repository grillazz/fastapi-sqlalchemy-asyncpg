import pytest
from fastapi import status
from httpx import AsyncClient
from inline_snapshot import snapshot
from dirty_equals import IsUUID

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from app.schemas.stuff import StuffSchema


pytestmark = pytest.mark.anyio

class StuffFactory(ModelFactory[StuffSchema]):
    __model__ = StuffSchema


async def test_add_stuff(client: AsyncClient):

    _stuff = StuffFactory.build(factory_use_constructors=True).model_dump(mode="json")[0],

    response = await client.post("/stuff", json=_stuff)
    print(response.json())
    assert response.status_code == status.HTTP_201_CREATED


    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": _stuff["name"],
            "description": _stuff["description"],
        }
    )


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {"name": "motorhead-0", "description": "we play rock and roll"},
            status.HTTP_200_OK,
        ),
    ),
)
async def test_get_stuff(client: AsyncClient, payload: dict, status_code: int):
    await client.post("/stuff", json=payload)
    name = payload["name"]
    response = await client.get(f"/stuff/{name}")
    assert response.status_code == status_code
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": "motorhead-0",
            "description": "we play rock and roll",
        }
    )





@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {"name": "motorhead-1", "description": "we play rock and roll"},
            status.HTTP_200_OK,
        ),
    ),
)
async def test_delete_stuff(client: AsyncClient, payload: dict, status_code: int):
    response = await client.post("/stuff", json=payload)
    name = response.json()["name"]
    response = await client.delete(f"/stuff/{name}")
    assert response.status_code == status_code
    assert response.json() == snapshot(True)


@pytest.mark.parametrize(
    "payload, status_code",
    (
        (
            {"name": "motorhead-2", "description": "we play rock and roll"},
            status.HTTP_200_OK,
        ),
    ),
)
@pytest.mark.parametrize(
    "patch_payload, patch_status_code",
    (
        (
            {"name": "motorhead-2", "description": "we play loud"},
            status.HTTP_200_OK,
        ),
    ),
)
async def test_update_stuff(
    client: AsyncClient,
    payload: dict,
    status_code: int,
    patch_payload: dict,
    patch_status_code: int,
):
    response = await client.post("/stuff", json=payload)
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": "motorhead-2",
            "description": "we play rock and roll",
        }
    )
    name = payload["name"]
    response = await client.patch(f"/stuff/{name}", json=patch_payload)
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": "motorhead-2",
            "description": "we play loud",
        }
    )
    assert response.status_code == patch_status_code
