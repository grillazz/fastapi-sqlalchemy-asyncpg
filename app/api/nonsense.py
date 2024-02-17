import io
from fastapi import APIRouter, Depends, status, UploadFile, HTTPException
from sqlalchemy.exc import SQLAlchemyError
import polars as pl
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.nonsense import Nonsense
from app.schemas.nnonsense import NonsenseResponse, NonsenseSchema

router = APIRouter(prefix="/v1/nonsense")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NonsenseResponse)
async def create_nonsense(payload: NonsenseSchema, db_session: AsyncSession = Depends(get_db)):
    nonsense = Nonsense(**payload.model_dump())
    await nonsense.save(db_session)
    return nonsense


@router.get("/", response_model=NonsenseResponse)
async def find_nonsense(
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await Nonsense.find(db_session, name)


@router.delete("/")
async def delete_nonsense(name: str, db_session: AsyncSession = Depends(get_db)):
    nonsense = await Nonsense.find(db_session, name)
    return await nonsense.delete(nonsense, db_session)


@router.patch("/", response_model=NonsenseResponse)
async def update_nonsense(
    payload: NonsenseSchema,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    nonsense = await Nonsense.find(db_session, name)
    await nonsense.update(db_session, **payload.model_dump())
    return nonsense


@router.post("/", response_model=NonsenseResponse)
async def merge_nonsense(
    payload: NonsenseSchema,
    db_session: AsyncSession = Depends(get_db),
):
    nonsense = Nonsense(**payload.model_dump())
    await nonsense.save_or_update(db_session)
    return nonsense


@router.post(
    "/import",
    status_code=status.HTTP_201_CREATED,
)
async def import_nonsense(
    xlsx: UploadFile,
    db_session: AsyncSession = Depends(get_db),
):
    file_bytes = await xlsx.read()

    nonsense_data = pl.read_excel(
        source=io.BytesIO(file_bytes),
        sheet_name="New Nonsense",
        engine="calamine",
    )

    try:
        nonsense_records = [
            Nonsense(
                name=nonsense.get("name"),
                description=nonsense.get("description"),
            )
            for nonsense in nonsense_data.to_dicts()
        ]
        db_session.add_all(nonsense_records)
        await db_session.commit()
        return {"filename": xlsx.filename, "nonsense_records": len(nonsense_records)}
    except (SQLAlchemyError, HTTPException) as ex:
        await db_session.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)) from ex
    finally:
        await db_session.close()
