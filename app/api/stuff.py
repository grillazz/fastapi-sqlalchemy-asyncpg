from fastapi import APIRouter, Depends, HTTPException, Request, status
from rotoger import AppStructLogger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stuff import RandomStuff, Stuff
from app.schemas.stuff import RandomStuff as RandomStuffSchema
from app.schemas.stuff import StuffResponse, StuffSchema

logger = AppStructLogger().get_logger()

router = APIRouter(prefix="/v1/stuff")


@router.post("/random", status_code=status.HTTP_201_CREATED)
async def create_random_stuff(
    payload: RandomStuffSchema, db_session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    random_stuff = RandomStuff(**payload.model_dump())
    await random_stuff.save(db_session)
    return {"id": str(random_stuff.id)}


@router.post("/add_many", status_code=status.HTTP_201_CREATED)
async def create_multi_stuff(
    payload: list[StuffSchema], db_session: AsyncSession = Depends(get_db)
):
    try:
        stuff_instances = [Stuff(**stuff.model_dump()) for stuff in payload]
        db_session.add_all(stuff_instances)
        await db_session.commit()
    except SQLAlchemyError as ex:
        await logger.aerror(f"Error inserting instances of Stuff: {repr(ex)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
        ) from ex
    else:
        await logger.ainfo(
            f"{len(stuff_instances)} Stuff instances inserted into the database."
        )
        return True


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StuffResponse)
async def create_stuff(
    payload: StuffSchema, db_session: AsyncSession = Depends(get_db)
):
    stuff = Stuff(**payload.model_dump())
    await stuff.save(db_session)
    return stuff


@router.get("/{name}", response_model=StuffResponse)
async def find_stuff(name: str, db_session: AsyncSession = Depends(get_db)):
    result = await Stuff.find(db_session, name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stuff with name {name} not found.",
        )
    return result


@router.get("/pool/{name}", response_model=StuffResponse)
async def find_stuff_pool(
    request: Request,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    """
    Asynchronous function to find a specific 'Stuff' object in the database using a connection pool.

    This function compiles an SQL statement to find a 'Stuff' object by its name, executes the statement
    using a connection from the application's connection pool, and returns the result as a dictionary.
    If the 'Stuff' object is not found, it raises an HTTPException with a 404 status code.
    If an SQLAlchemyError occurs during the execution of the SQL statement, it raises an HTTPException
    with a 422 status code.

    Args:
        request (Request): The incoming request. Used to access the application's connection pool.
        name (str): The name of the 'Stuff' object to find.
        db_session (AsyncSession): The database session. Used to compile the SQL statement.

    Returns:
        dict: The found 'Stuff' object as a dictionary.

    Raises:
        HTTPException: If the 'Stuff' object is not found or an SQLAlchemyError occurs.
    """
    try:
        stmt = await Stuff.find(db_session, name, compile_sql=True)
        result = await request.app.postgres_pool.fetchrow(str(stmt))
    except SQLAlchemyError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)
        ) from ex
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stuff with name {name} not found.",
        )
    return dict(result)


@router.delete("/{name}")
async def delete_stuff(name: str, db_session: AsyncSession = Depends(get_db)):
    stuff = await Stuff.find(db_session, name)
    return await Stuff.delete(stuff, db_session)


@router.patch("/{name}", response_model=StuffResponse)
async def update_stuff(
    payload: StuffSchema,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    stuff = await Stuff.find(db_session, name)
    await stuff.update(**payload.model_dump())
    return stuff
