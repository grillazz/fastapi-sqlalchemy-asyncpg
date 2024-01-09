import pytest
from httpx import AsyncClient
from starlette import status
import jwt

pytestmark = pytest.mark.anyio


# TODO: parametrize test with diff urls
async def test_add_user(client: AsyncClient):
    payload = {"email": "joe@grillazz.com", "first_name": "Joe", "last_name": "Garcia", "password": "s1lly"}
    response = await client.post("/user/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    claimset = jwt.decode(response.json()["access_token"], options={"verify_signature": False})
    assert claimset["email"] == payload["email"]
    assert claimset["expiry"] > 0
    assert claimset["platform"] == "python-httpx/0.26.0"


# TODO: parametrize test with diff urls including 404 and 401
async def test_get_token(client: AsyncClient):
    payload = {"email": "joe@grillazz.com", "password": "s1lly"}
    response = await client.post("/user/token", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    claimset = jwt.decode(response.json()["access_token"], options={"verify_signature": False})
    assert claimset["email"] == payload["email"]
    assert claimset["expiry"] > 0
    assert claimset["platform"] == "python-httpx/0.26.0"


# TODO: baerer token test
# TODO: > get token > test endpoint auth with token > expire token on redis > test endpoint auth with token
