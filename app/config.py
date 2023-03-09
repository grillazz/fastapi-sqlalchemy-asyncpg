import os
from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        user=os.getenv("SQL_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("SQL_HOST"),
        port="5432",
        path=f"/{os.getenv('SQL_DB') or ''}",
    )


@lru_cache
def get_settings():
    return Settings()
