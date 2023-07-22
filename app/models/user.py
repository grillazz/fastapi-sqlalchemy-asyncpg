import uuid
from typing import Any

from cryptography.fernet import Fernet
from sqlalchemy import Column, String, LargeBinary, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.models.base import Base

global_settings = config.get_settings()

cipher_suite = Fernet(global_settings.secret_key)


class User(Base):  # type: ignore
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid.uuid4,
        primary_key=True,
    )
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    _password = Column("password", LargeBinary, nullable=False)

    def __init__(self, email: str, first_name: str, last_name: str, password: str = None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password

    @property
    def password(self):
        return cipher_suite.decrypt(self._password).decode()

    @password.setter
    def password(self, password: str):
        self._password = cipher_suite.encrypt(password.encode())

    def check_password(self, password: str):
        return self.password == password

    @classmethod
    async def find(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()
