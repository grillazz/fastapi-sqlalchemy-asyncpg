import logging
import os
from functools import lru_cache

from pydantic import BaseSettings

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    """

    BaseSettings, from Pydantic, validates the data so that when we create an instance of Settings,
     environment and testing will have types of str and bool, respectively.

    Parameters:
    pg_user (str):
    pg_pass (str):
    pg_database: (str):
    pg_test_database: (str):
    asyncpg_url: AnyUrl:
    asyncpg_test_url: AnyUrl:

    Returns:
    instance of Settings

    """

    pg_user: str = os.getenv("POSTGRES_USER", "")
    pg_pass: str = os.getenv("POSTGRES_PASS", "")
    pg_host: str = os.getenv("POSTGRES_HOST", "")
    pg_database: str = os.getenv("POSTGRES_DB", "")
    pg_test_database: str = os.getenv("POSTGRES_TEST_DB", "")
    asyncpg_url: str = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_database}"
    asyncpg_test_url: str = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_test_database}"


@lru_cache()
def get_settings():
    log.info("Loading config settings from the environment...")
    return Settings()
