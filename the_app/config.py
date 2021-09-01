import os
from functools import lru_cache

from pydantic import BaseSettings

from the_app.utils import get_logger

logger = get_logger(__name__)


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

    pg_user: str = os.getenv("SQL_USER", "")
    pg_pass: str = os.getenv("POSTGRES_PASSWORD", "")
    pg_host: str = os.getenv("SQL_HOST", "")
    pg_database: str = os.getenv("SQL_DB", "")
    pg_test_database: str = os.getenv("SQL_TEST_DB", "")
    asyncpg_url: str = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_database}"
    asyncpg_test_url: str = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_test_database}"

    jwt_secret_key: str = os.getenv("SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("ALGORITHM", "")
    jwt_access_toke_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1)


@lru_cache()
def get_settings():
    logger.info("Loading config settings from the environment...")
    return Settings()
