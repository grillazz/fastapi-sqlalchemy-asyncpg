import uuid
from typing import Any

import bcrypt
from pydantic import SecretStr
from sqlalchemy import Column, LargeBinary, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    _password: bytes = Column(LargeBinary, nullable=False)

    @property
    def password(self):
        return self._password.decode("utf-8")

    @password.setter
    def password(self, password: SecretStr):
        _password_string = password.get_secret_value().encode("utf-8")
        self._password = bcrypt.hashpw(_password_string, bcrypt.gensalt())

    def check_password(self, password: SecretStr):
        return bcrypt.checkpw(
            password.get_secret_value().encode("utf-8"), self._password
        )

    @classmethod
    async def find(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()
