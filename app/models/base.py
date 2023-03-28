from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class BaseReadOnly:
    id: Any
    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()


@as_declarative()
class Base:
    id: Any
    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    async def save(self, db_session: AsyncSession):
        """

        :param db_session:
        :return:
        """
        try:
            db_session.add(self)
            return await db_session.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    async def delete(self, db_session: AsyncSession):
        """

        :param db_session:
        :return:
        """
        try:
            await db_session.delete(self)
            await db_session.commit()
            return True
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
            ) from ex

    async def update(self, db_session: AsyncSession, **kwargs):
        """

        :param db_session:
        :param kwargs:
        :return:
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        await self.save(db_session)

    async def save_or_update(self, db: AsyncSession):
        # TODO: this will be successor of update meth
        _success = False
        try:
            db.add(self)
            _success = await db.commit()
            return _success
        except IntegrityError as exception:
            if not _success:
                # TODO: check if exception is instance of class 'asyncpg.exceptions.UniqueViolationError'
                return await db.merge(self)
            else:
                raise exception
        finally:
            await db.close()