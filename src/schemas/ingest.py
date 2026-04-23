from pydantic import BaseModel


class IngestResponse(BaseModel):
    filename: str
    chunks_indexed: int