from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from the_app.database import get_db
from the_app.models.stuff import Stuff
from the_app.schemas.stuff import StuffResponse, StuffSchema

router = APIRouter(prefix="/v1/stuff")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StuffResponse)
async def create_stuff(payload: StuffSchema, db_session: AsyncSession = Depends(get_db)):
    stuff = Stuff(**payload.dict())
    await stuff.save(db_session)
    return stuff


@router.get("/", response_model=StuffResponse)
async def find_stuff(
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await Stuff.find(db_session, name)


@router.delete("/")
async def delete_stuff(name: str, db_session: AsyncSession = Depends(get_db)):
    stuff = await Stuff.find(db_session, name)
    return await Stuff.delete(stuff, db_session)


@router.patch("/", response_model=StuffResponse)
async def update_stuff(
    payload: StuffSchema,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    stuff = await Stuff.find(db_session, name)
    await stuff.update(db_session, **payload.dict())
    return stuff
