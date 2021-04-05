from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from the_app.database import get_db
from the_app.models.stuff import Stuff
from the_app.schemas.stuff import StuffResponse, StuffSchema

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StuffResponse)
async def create_stuff(stuff: StuffSchema, db_session: AsyncSession = Depends(get_db)):
    stuff_instance = await Stuff.create(db_session, stuff)
    return stuff_instance


@router.get("/", response_model=StuffResponse)
async def find_stuff(
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    stuff_instance = await Stuff.find(db_session, name)
    return stuff_instance


@router.delete("/")
async def delete_stuff(name: str, db_session: AsyncSession = Depends(get_db)):
    stuff_instance = await Stuff.find(db_session, name)
    return await Stuff.delete(stuff_instance, db_session)


@router.patch("/", response_model=StuffResponse)
async def update_stuff(
    stuff: StuffSchema,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    stuff_instance = await Stuff.find(db_session, name)
    stuff_instance = await stuff_instance.update(db_session, stuff)
    return stuff_instance
