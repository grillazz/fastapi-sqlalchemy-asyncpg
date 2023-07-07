import os
from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn = os.getenv("SQL_URL")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
