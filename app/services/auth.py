"""Bearer-token authentication and Redis-backed token storage."""

import time

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from rotoger import get_logger

from app.config import settings as global_settings
from app.models.user import User

logger = get_logger()


async def get_from_redis(request: Request, key: str) -> str | None:
    """Return the Redis value stored under ``key``."""
    return await request.app.redis.get(key)


async def set_to_redis(request: Request, key: str, value: str, ex: int) -> bool:
    """Store ``value`` in Redis for ``ex`` seconds."""
    return await request.app.redis.set(key, value, ex=ex)


async def verify_jwt(request: Request, token: str) -> bool:
    """Check whether Redis recognizes the bearer token."""
    payload = await get_from_redis(request, token)
    return bool(payload)


class AuthBearer(HTTPBearer):
    """Validate bearer credentials against the active Redis token store."""

    async def __call__(self, request: Request) -> str:
        """Return a valid token or raise an authorization error."""
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=403, detail="Invalid authentication scheme."
            )
        if not await verify_jwt(request, credentials.credentials):
            raise HTTPException(
                status_code=403, detail="Invalid token or expired token."
            )
        await logger.ainfo(f"Token verified: {credentials.credentials}")
        return credentials.credentials


async def create_access_token(user: User, request: Request) -> str | None:
    """Sign a user token and store it in Redis until its configured expiry."""
    payload = {
        "email": user.email,
        "expiry": time.time() + global_settings.jwt_expire,
        "platform": request.headers.get("User-Agent"),
    }
    token = jwt.encode(
        payload, str(user.password), algorithm=global_settings.jwt_algorithm
    )

    stored = await set_to_redis(
        request, token, str(payload), ex=global_settings.jwt_expire
    )
    if stored:
        return token
