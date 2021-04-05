import uuid

from sqlalchemy import Column, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from the_app.models.base import Base
from the_app.schemas.stuff import StuffSchema


class Stuff(Base):
    __tablename__ = "stuff"
    id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, autoincrement=True)
    name = Column(String, nullable=False, primary_key=True, unique=True)
    description = Column(String, nullable=False)

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @classmethod
    async def create(cls, db_session: AsyncSession, schema: StuffSchema):
        stuff = Stuff(
            name=schema.name,
            description=schema.description,
        )
        await stuff.save(db_session)
        return stuff

    async def update(self, db_session: AsyncSession, schema: StuffSchema):
        self.name = schema.name
        self.description = schema.description
        await self.save(db_session)
        return self

    @classmethod
    async def find(cls, db_session: AsyncSession, name: str):
        stmt = select(cls).where(cls.name == name)
        result = await db_session.execute(stmt)
        return result.scalars().first()
