from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from the_app.database import get_db
from the_app.models.stuff import Stuff
from the_app.schemas.stuff import StuffResponse, StuffSchema

router = APIRouter()


@router.post("/", response_model=StuffResponse)
async def create_stuff(stuff: StuffSchema, db_session: AsyncSession = Depends(get_db)):
    stuff_id = await Stuff.create(db_session, stuff)
    return {**stuff.dict(), "id": stuff_id}


@router.delete("/")
async def delete_stuff(stuff_id: UUID, db_session: AsyncSession = Depends(get_db)):
    return await Stuff.delete(db_session, stuff_id)


@router.get("/")
async def find_stuff(
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await Stuff.find(db_session, name)


@router.patch("/")
async def update_config(
    stuff: StuffSchema,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    instance_of_the_stuff = await Stuff.find(db_session, name)
    return instance_of_the_stuff.update(db_session, stuff)
