from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.shakespeare import Paragraph

router = APIRouter(prefix="/v1/shakespeare")


@router.get(
    "/",
)
@cache(namespace="test-2", expire=60)
async def find_paragraph(
    character: Annotated[str, Query(description="Character name")],
    db_session: AsyncSession = Depends(get_db),
):
    return await Paragraph.find(db_session=db_session, character=character)
