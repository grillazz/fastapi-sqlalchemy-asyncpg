import uuid

from fastapi import HTTPException, status
from sqlalchemy import Column, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from the_app.models.base import Base


class Stuff(Base):
    __tablename__ = "stuff"
    id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, autoincrement=True)
    name = Column(String, nullable=False, primary_key=True, unique=True)
    description = Column(String, nullable=False)

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @classmethod
    async def find(cls, db_session: AsyncSession, name: str):
        stmt = select(cls).where(cls.name == name)
        result = await db_session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"Record not found": f"There is no record for requested name value : {name}"},
            )
        else:
            return instance
