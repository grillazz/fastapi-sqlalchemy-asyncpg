import io

import polars as pl
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.nonsense import Nonsense
from app.schemas.nnonsense import NonsenseResponse, NonsenseSchema

router = APIRouter(prefix="/v1/nonsense")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NonsenseResponse)
async def create_nonsense(
    payload: NonsenseSchema, db_session: AsyncSession = Depends(get_db)
):
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
        ) from ex
    finally:
        # Ensure that the database session is closed, regardless of whether an error occurred or not
        await db_session.close()


# TODO: add websocket to full text search postgres database for nonsense description

# To add a WebSocket to full text search a PostgreSQL database for the `nonsense` description, you can use the `websockets` library in Python. Here's a step-by-step plan:
#
# 1. Install the `websockets` library if you haven't done so already.
# 2. Create a new WebSocket route in your FastAPI application.
# 3. In the WebSocket route, accept a search query from the client.
# 4. Use the search query to perform a full text search on the `nonsense` table in your PostgreSQL database.
# 5. Send the search results back to the client through the WebSocket connection.
#
# Here's how you can implement this:
#
# ```python
# import websockets
# from fastapi import WebSocket
# from sqlalchemy import text
#
# router = APIRouter()
#
# @router.websocket("/ws/nonsense")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         query = text(f"""
#             SELECT * FROM nonsense
#             WHERE to_tsvector('english', description) @@ plainto_tsquery('english', :q)
#         """)
#         result = await db_session.execute(query, {"q": data})
#         await websocket.send_json(result.fetchall())
# # ```
#
# This code creates a new WebSocket route at `/ws/nonsense`. When a client connects to this route and sends a message, the message is used as a search query in a full text search on the `nonsense` table. The search results are then sent back to the client through the WebSocket connection.
#
# Please note that this is a basic implementation and might need adjustments based on your specific needs. For example, you might want to add error handling, handle disconnections, or format the search results before sending them back to the client.
#

# TODO: https://medium.com/@amitosh/full-text-search-fts-with-postgresql-and-sqlalchemy-edc436330a0c
# TODO: https://www.postgresql.org/docs/13/textsearch-intro.html
