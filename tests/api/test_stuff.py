import pytest
from fastapi import status
from httpx import AsyncClient
from inline_snapshot import snapshot
from dirty_equals import IsUUID

from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas.stuff import StuffSchema

pytestmark = pytest.mark.anyio


class StuffFactory(ModelFactory[StuffSchema]):
    __model__ = StuffSchema


async def test_add_stuff(client: AsyncClient):
    stuff = StuffFactory.build(factory_use_constructors=True).model_dump(mode="json")
    response = await client.post("/stuff", json=stuff)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": stuff["name"],
            "description": stuff["description"],
        }
    )


async def test_get_stuff(client: AsyncClient):
    stuff = StuffFactory.build(factory_use_constructors=True).model_dump(mode="json")
    await client.post("/stuff", json=stuff)
    name = stuff["name"]
    response = await client.get(f"/stuff/{name}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": stuff["name"],
            "description": stuff["description"],
        }
    )


async def test_delete_stuff(client: AsyncClient):
    stuff = StuffFactory.build(factory_use_constructors=True).model_dump(mode="json")
    await client.post("/stuff", json=stuff)
    name = stuff["name"]
    response = await client.delete(f"/stuff/{name}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == snapshot(True)


async def test_update_stuff(client: AsyncClient):
    stuff = StuffFactory.build(factory_use_constructors=True).model_dump(mode="json")
    response = await client.post("/stuff", json=stuff)
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": stuff["name"],
            "description": stuff["description"],
        }
    )
    name = stuff["name"]
    response = await client.patch(
        f"/stuff/{name}",
        json={"name": stuff["name"], "description": "we play rock and roll"},
    )
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "name": stuff["name"],
            "description": "we play rock and roll",
        }
    )
    assert response.status_code == status.HTTP_200_OK
