import os

from pydantic import PostgresDsn, RedisDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )
    redis_url: RedisDsn = os.getenv("REDIS_URL")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expire: int = os.getenv("JWT_EXPIRE")

    SQL_USER: str
    SQL_PASS: str
    SQL_HOST: str
    SQL_DB: str

    @computed_field
    @property
    def asyncpg_url(self) -> PostgresDsn:
        """
        This is a computed field that generates a PostgresDsn URL for asyncpg.

        The URL is built using the MultiHostUrl.build method, which takes the following parameters:
        - scheme: The scheme of the URL. In this case, it is "postgresql+asyncpg".
        - username: The username for the SQL database, retrieved from the SQL_USER environment variable.
        - password: The password for the SQL database, retrieved from the SQL_PASS environment variable.
        - host: The host of the SQL database, retrieved from the SQL_HOST environment variable.
        - path: The path of the SQL database, retrieved from the SQL_DB environment variable.

        Returns:
            PostgresDsn: The constructed PostgresDsn URL for asyncpg.
        """
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.SQL_USER,
            password=self.SQL_PASS,
            host=self.SQL_HOST,
            path=self.SQL_DB,
        )


settings = Settings()
