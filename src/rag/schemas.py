from pydantic import BaseModel, ConfigDict, Field


class Chunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str = Field(..., min_length=1)
    index: int = Field(..., ge=0, description="Index of chunk in document")
    source: str = Field(..., description="Source (filename, URL and etc.)")

    def __len__(self) -> int:
        return len(self.text)

class SearchResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    chunk: Chunk
    score: float = Field(..., ge=0.0, le=1.0)