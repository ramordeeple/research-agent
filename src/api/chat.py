import logging

from fastapi import APIRouter, status

from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import process_chat

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest) -> ChatResponse:
    answer, sources = await process_chat(request.message)
    return ChatResponse(answer=answer, sources=sources)