from pydantic import BaseModel, Field

from src.core.constants import CHAT_MIN_LENGTH, CHAT_MAX_LENGTH


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=CHAT_MIN_LENGTH, max_length=CHAT_MAX_LENGTH)

class Source(BaseModel):
    text: str
    source: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] = []
