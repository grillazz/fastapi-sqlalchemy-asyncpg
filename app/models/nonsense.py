import uuid

from fastapi import HTTPException, status
from sqlalchemy import String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Nonsense(Base):
    __tablename__ = "nonsense"
    __table_args__ = ({"schema": "happy_hog"},)
    id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid.uuid4, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    description: Mapped[str | None]
    # TODO: apply relation to other tables

    @classmethod
    async def get_by_name(cls, db_session: AsyncSession, name: str):
        stmt = select(cls).where(cls.name == name)
        result = await db_session.execute(stmt)
        instance = result.scalars().first()
        return instance


