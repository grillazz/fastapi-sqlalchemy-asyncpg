import uuid

from fastapi import HTTPException, status
from sqlalchemy import String, select, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped, relationship, joinedload

from app.models.base import Base
from app.models.nonsense import Nonsense


class Stuff(Base):
    __tablename__ = "stuff"
    __table_args__ = ({"schema": "happy_hog"},)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid.uuid4, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    description: Mapped[str | None]

    nonsense: Mapped["Nonsense"] = relationship(
        "Nonsense", secondary="happy_hog.stuff_full_of_nonsense"
    )

    @classmethod
    async def find(cls, db_session: AsyncSession, name: str, compile_sql: bool = False):
        stmt = select(cls).options(joinedload(cls.nonsense)).where(cls.name == name)
        if compile_sql:
            return stmt.compile(compile_kwargs={"literal_binds": True})
        result = await db_session.execute(stmt)
        return result.scalars().first()


class StuffFullOfNonsense(Base):
    __tablename__ = "stuff_full_of_nonsense"
    __table_args__ = ({"schema": "happy_hog"},)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    stuff_id: Mapped[Stuff] = mapped_column(UUID, ForeignKey("happy_hog.stuff.id"))
    nonsense_id: Mapped["Nonsense"] = mapped_column(
        UUID, ForeignKey("happy_hog.nonsense.id")
    )
    but_why: Mapped[str | None]
