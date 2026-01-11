import jwt
import pytest
from dirty_equals import IsPositiveFloat, IsStr, IsUUID
from httpx import AsyncClient
from inline_snapshot import snapshot
from starlette import status

pytestmark = pytest.mark.anyio


# TODO: parametrize test with diff urls
async def test_add_user(client: AsyncClient):
    payload = {
        "email": "joe@grillazz.com",
        "first_name": "Joe",
        "last_name": "Garcia",
        "password": "s1lly",
    }
    response = await client.post("/user/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == snapshot(
        {
            "id": IsUUID(4),
            "email": "joe@grillazz.com",
            "first_name": "Joe",
            "last_name": "Garcia",
            "access_token": IsStr(),
        }
    )

    claimset = jwt.decode(
        response.json()["access_token"], options={"verify_signature": False}
    )
    assert claimset["expiry"] == IsPositiveFloat()
    assert claimset["platform"] == "python-httpx/0.28.1"


# TODO: parametrize test with diff urls including 404 and 401
async def test_get_token(client: AsyncClient):
    # Create the user first
    user_payload = {
        "email": "joe@grillazz.com",
        "first_name": "Joe",
        "last_name": "Garcia",
        "password": "s1lly",
    }
    create_user_response = await client.post("/user/", json=user_payload)
    assert create_user_response.status_code == status.HTTP_201_CREATED

    # Now request the token
    token_payload = {"email": "joe@grillazz.com", "password": "s1lly"}
    response = await client.post(
        "/user/token",
        data=token_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    claimset = jwt.decode(
        response.json()["access_token"], options={"verify_signature": False}
    )
    assert claimset["email"] == token_payload["email"]
    assert claimset["expiry"] == IsPositiveFloat()
    assert claimset["platform"] == "python-httpx/0.28.1"


# TODO: baerer token test
# TODO: > get token > test endpoint auth with token > expire token on redis > test endpoint auth with token
