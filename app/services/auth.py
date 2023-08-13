import time
import jwt

from app import config
from app.models.user import User

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

global_settings = config.get_settings()


async def verify_jwt(request: Request, token: str) -> bool:
    _payload = await request.app.state.redis.get(token)
    if _payload:
        return True
    else:
        return False


class AuthBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not await verify_jwt(request, credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


async def create_access_token(user: User, request: Request):
    _payload = {
        "email": user.email,
        "expiry": time.time() + global_settings.jwt_expire,
        "platform": request.headers.get("User-Agent"),
    }
    _token = jwt.encode(_payload, str(user.password), algorithm=global_settings.jwt_algorithm)

    _bool = await request.app.state.redis.set(_token, str(_payload), ex=global_settings.jwt_expire)
    if _bool:
        return _token
