import logging

from fastapi import APIRouter

from src.schemas.chat import ChatResponse, ChatRequest
from src.services.chat_service import process_chat

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    answer = await process_chat(request.message)

    return ChatResponse(answer=answer)