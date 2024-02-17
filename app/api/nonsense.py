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
    """
    This function is a FastAPI route handler that imports data from an Excel file into a database.

    Args:
        xlsx (UploadFile): The Excel file that will be uploaded by the client.
        db_session (AsyncSession): A SQLAlchemy session for interacting with the database.

    Returns:
        dict: A dictionary containing the filename and the number of imported records.

    Raises:
        HTTPException: If an error occurs during the process (either a SQLAlchemy error or an HTTP exception),
                       the function rolls back the session and raises an HTTP exception with a 422 status code.
    """
    try:
        # Read the uploaded file into bytes
        file_bytes = await xlsx.read()

        # Use the `polars` library to read the Excel data into a DataFrame
        nonsense_data = pl.read_excel(
            source=io.BytesIO(file_bytes),
            sheet_name="New Nonsense",
            engine="calamine",
        )
        # Iterate over the DataFrame rows and create a list of `Nonsense` objects
        nonsense_records = [
            Nonsense(
                name=nonsense.get("name"),
                description=nonsense.get("description"),
            )
            for nonsense in nonsense_data.to_dicts()
        ]
        # Add all the `Nonsense` objects to the SQLAlchemy session
        db_session.add_all(nonsense_records)
        # Commit the session to save the objects to the database
        await db_session.commit()
        # Return a JSON response containing the filename and the number of imported records
        return {"filename": xlsx.filename, "nonsense_records": len(nonsense_records)}
    except (SQLAlchemyError, HTTPException, ValueError) as ex:
        # If an error occurs, roll back the session
        await db_session.rollback()
        # Raise an HTTP exception with a 422 status code
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)) from ex
    finally:
        # Ensure that the database session is closed, regardless of whether an error occurred or not
        await db_session.close()
