from pydantic import BaseModel, Field

from src.core.constants import DEFAULT_TOP_K
from src.rag.retriever import retrieve
from src.tools.base import Tool


class RagSearchInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant content in uploaded documents")
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20)


class RagSearchTool(Tool):
    @property
    def name(self) -> str:
        return "rag_search"

    @property
    def description(self) -> str:
        return (
            "Searches loaded documents for information relevant to the query. "
            "Use this when the user asks about specific content in uploaded documents. "
            "Returns relevant text excerpts with their source filenames."
        )

    @property
    def input_schema(self) -> type[BaseModel]:
        return RagSearchInput

    def execute(self, input_data: BaseModel) -> str:
        if not isinstance(input_data, RagSearchInput):
            return "Invalid input: expected RagSearchInput"

        results = retrieve(input_data.query, top_k=input_data.top_k)

        if not results:
            return "No relevant documents found."

        formatted_chunks = []
        for i, result in enumerate(results, 1):
            formatted_chunks.append(
                f"[{i}] Source: {result.chunk.source} (relevance: {result.score:.2f})\n"
                f"{result.chunk.text}"
            )

        return "\n\n".join(formatted_chunks)