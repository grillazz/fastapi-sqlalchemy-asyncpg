from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.shakespeare import Paragraph

router = APIRouter(prefix="/v1/shakespeare")


@router.get("/",)
async def find_paragraph(
    character: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await Paragraph.find(db_session=db_session, character=character)
