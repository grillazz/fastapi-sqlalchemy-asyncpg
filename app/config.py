import os
from typing import Literal

from pydantic import BaseModel, PostgresDsn, RedisDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class SMTPConfig(BaseModel):
    server: str = os.getenv("EMAIL_HOST", "smtp_server")
    port: int = os.getenv("EMAIL_PORT", 587)
    username: str = os.getenv("EMAIL_HOST_USER", "smtp_user")
    password: str = os.getenv("EMAIL_HOST_PASSWORD", "smtp_password")
    template_path: str = os.getenv("EMAIL_TEMPLATE_PATH", "templates")


class ChatConfig(BaseModel):
    """Configuration for the websocket chat service's model-client adapter.

    ``backend`` selects which :class:`~app.services.chat_agent.ChatAgent`
    implementation is built by
    :func:`~app.services.chat_agent.build_chat_agent` during app startup:

    - ``"stub"``: a local, dependency-free echo agent (default, no network
      calls, ideal for local dev/tests).
    - ``"ollama"``: streams completions from an OpenAI-compatible endpoint
      (e.g. a local Ollama server), reusing the same adapter interface.
    """

    backend: Literal["stub", "ollama"] = os.getenv("CHAT_BACKEND", "stub")
    base_url: str = os.getenv("CHAT_BASE_URL", "http://localhost:11434/v1")
    model: str = os.getenv("CHAT_MODEL", "llama3.2")
    stream_delay_seconds: float = float(os.getenv("CHAT_STREAM_DELAY", "0.02"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expire: int = os.getenv("JWT_EXPIRE")

    smtp: SMTPConfig = SMTPConfig()
    chat: ChatConfig = ChatConfig()

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: str

    JWT_ALGORITHM: str
    JWT_EXPIRE: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_TEST_DB: str

    @computed_field
    @property
    def redis_url(self) -> RedisDsn:
        """
        This is a computed field that generates a RedisDsn URL for redis-py.

        The URL is built using the MultiHostUrl.build method, which takes the following parameters:
        - scheme: The scheme of the URL. In this case, it is "redis".
        - host: The host of the Redis database, retrieved from the REDIS_HOST environment variable.
        - port: The port of the Redis database, retrieved from the REDIS_PORT environment variable.
        - path: The path of the Redis database, retrieved from the REDIS_DB environment variable.

        Returns:
            RedisDsn: The constructed RedisDsn URL for redis-py.
        """
        return MultiHostUrl.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=self.REDIS_DB,
        )

    @computed_field
    @property
    def asyncpg_url(self) -> PostgresDsn:
        """
        This is a computed field that generates a PostgresDsn URL for asyncpg.

        The URL is built using the MultiHostUrl.build method, which takes the following parameters:
        - scheme: The scheme of the URL. In this case, it is "postgresql+asyncpg".
        - username: The username for the Postgres database, retrieved from the POSTGRES_USER environment variable.
        - password: The password for the Postgres database, retrieved from the POSTGRES_PASSWORD environment variable.
        - host: The host of the Postgres database, retrieved from the POSTGRES_HOST environment variable.
        - path: The path of the Postgres database, retrieved from the POSTGRES_DB environment variable.

        Returns:
            PostgresDsn: The constructed PostgresDsn URL for asyncpg.
        """
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def test_asyncpg_url(self) -> PostgresDsn:
        """
        This is a computed field that generates a PostgresDsn URL for the test database using asyncpg.

        The URL is built using the MultiHostUrl.build method, which takes the following parameters:
        - scheme: The scheme of the URL. In this case, it is "postgresql+asyncpg".
        - username: The username for the Postgres database, retrieved from the POSTGRES_USER environment variable.
        - password: The password for the Postgres database, retrieved from the POSTGRES_PASSWORD environment variable.
        - host: The host of the Postgres database, retrieved from the POSTGRES_HOST environment variable.
        - path: The path of the Postgres test database, retrieved from the POSTGRES_TEST_DB environment variable.

        Returns:
            PostgresDsn: The constructed PostgresDsn URL for the test database with asyncpg.
        """
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=self.POSTGRES_TEST_DB,
        )

    @computed_field
    @property
    def postgres_url(self) -> PostgresDsn:
        """
        This is a computed field that generates a PostgresDsn URL

        The URL is built using the MultiHostUrl.build method, which takes the following parameters:
        - scheme: The scheme of the URL. In this case, it is "postgres".
        - username: The username for the Postgres database, retrieved from the POSTGRES_USER environment variable.
        - password: The password for the Postgres database, retrieved from the POSTGRES_PASSWORD environment variable.
        - host: The host of the Postgres database, retrieved from the POSTGRES_HOST environment variable.
        - path: The path of the Postgres database, retrieved from the POSTGRES_DB environment variable.

        Returns:
            PostgresDsn: The constructed PostgresDsn URL.
        """
        return MultiHostUrl.build(
            scheme="postgres",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            path=self.POSTGRES_DB,
        )


settings = Settings()
