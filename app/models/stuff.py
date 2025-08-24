import uuid

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

from app.models.base import Base
from app.models.nonsense import Nonsense
from app.utils.decorators import compile_sql_or_scalar


class RandomStuff(Base):
    __tablename__ = "random_stuff"
    __table_args__ = ({"schema": "happy_hog"},)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    chaos: Mapped[dict] = mapped_column(JSON)


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
    @compile_sql_or_scalar
    async def get_by_name(cls, db_session: AsyncSession, name: str, compile_sql=False):
        stmt = select(cls).options(joinedload(cls.nonsense)).where(cls.name == name)
        return stmt


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
