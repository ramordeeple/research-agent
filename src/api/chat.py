import logging

from fastapi import APIRouter, status

from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import process_chat

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await process_chat(request)