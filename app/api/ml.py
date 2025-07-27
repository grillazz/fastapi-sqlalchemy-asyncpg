from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse

from app.services.llm import get_llm_service
from rotoger import AppStructLogger

logger = AppStructLogger().get_logger()

router = APIRouter()


@router.post("/chat/")
async def chat(prompt: Annotated[str, Form()], llm_service=Depends(get_llm_service)):
    return StreamingResponse(llm_service.stream_chat(prompt), media_type="text/plain")
