import os
from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn = os.getenv("SQL_URL")
    secret_key: str = os.getenv("FERNET_KEY")
    redis_url: RedisDsn = os.getenv("REDIS_URL")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expire: int = os.getenv("JWT_EXPIRE")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
