import uuid
from typing import Any

import bcrypt
from passlib.context import CryptContext
from sqlalchemy import Column, String, LargeBinary, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app import config
from app.models.base import Base

global_settings = config.get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        return self._password.decode("utf-8")

    @password.setter
    def password(self, password: str):
        self._password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password: str):
        return pwd_context.verify(password, self.password)

    @classmethod
    async def find(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()
