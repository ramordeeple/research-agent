from pydantic import BaseModel, Field

from src.llm.schemas import Message


class Session(BaseModel):
    session_id: str
    messages: list[Message] = Field(default_factory=list)