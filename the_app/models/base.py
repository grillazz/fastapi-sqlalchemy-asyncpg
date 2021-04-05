from typing import Any

from fastapi import HTTPException, status
from icecream import ic
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    async def save(self, db_session: AsyncSession):
        try:
            db_session.add(self)
            return await db_session.commit()
        except SQLAlchemyError as ex:
            ic("Have to rollback, save failed:")
            ic(ex)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.__str__())

    async def delete(self, db_session: AsyncSession):
        try:
            await db_session.delete(self)
            await db_session.commit()
            return True
        except SQLAlchemyError as ex:
            ic("Have to rollback, save failed:")
            ic(ex)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.__str__())
