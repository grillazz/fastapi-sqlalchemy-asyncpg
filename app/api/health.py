import logging

from fastapi import APIRouter, status, Request

router = APIRouter()


@router.get("/redis", status_code=status.HTTP_200_OK)
async def redis_check(request: Request):
    _redis = await request.app.state.redis
    _info = None
    try:
        _info = await _redis.info()
    except Exception as e:
        logging.error(f"Redis error: {e}")
    return _info
