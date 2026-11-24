# AI Research Agent

Upload PDF, plain text, or Markdown documents and ask questions about them. The agent indexes document chunks in Qdrant and can cite relevant excerpts in its answers. It also answers general questions directly.

## Features

- Document ingestion with automatic chunking and local embeddings from fastembed (BGE-small-en-v1.5, 384 dimensions)
- A ReAct loop that calls `rag_search` when the agent needs information from uploaded documents
- A FastAPI interface with chat, ingestion, and health endpoints
- An OpenAI-compatible LLM client configured for Gemini by default
- A multi-stage Docker build with a non-root runtime user and a preloaded embedding model

## Quick start with Docker

You need Docker Compose, [uv](https://docs.astral.sh/uv/) to generate the lockfile if it is missing, and a Gemini API key from [Google AI Studio](https://aistudio.google.com).

1. Copy the example configuration and set `LLM_API_KEY` in `.env`.

   ```bash
   cp .env.example .env
   ```

2. If the checkout lacks `uv.lock`, run `uv lock`. The Docker build uses this file to install dependencies.
3. Start the app and Qdrant.

   ```bash
   docker compose up --build
   ```

4. Open [Swagger UI](http://localhost:8000/docs). Use `POST /api/v1/ingest` to upload a document, then ask about it using `POST /api/v1/chat`.

## API

### `GET /api/v1/health`

Checks whether the app responds.

```json
{"status": 200}
```

### `POST /api/v1/ingest`

Upload a `.pdf`, `.txt`, or `.md` file as multipart form data.

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F 'file=@document.pdf'
```

Example response

```json
{
  "filename": "document.pdf",
  "chunks_indexed": 42
}
```

### `POST /api/v1/chat`

Send a question as JSON. Include the returned `session_id` in a follow-up request to reuse the conversation history. History is held in memory for the lifetime of the app process.

```json
{
  "message": "How long did the study last?"
}
```

Example response for a document-backed answer

```json
{
  "answer": "The study lasted 12 weeks.",
  "sources": [
    {
      "source": "document.pdf",
      "score": 0.87,
      "text": "The study lasted 12 weeks."
    }
  ],
  "session_id": "69398804-149f-4c02-9114-81902b5a6e22"
}
```

Direct answers return an empty `sources` list.

## Local development

The project targets Python 3.12. With `.env` configured, start Qdrant and run the app with uv.

```bash
docker compose up -d qdrant
uv sync
uv run uvicorn src.main:app --reload
```

```bash
uv run pytest -v
uv run ruff check src tests
uv run ruff format src tests
```

The full test suite uses Qdrant, a valid LLM API key, and the embedding model. If the model is missing from the local cache, fastembed downloads it on first use. Some Qdrant-dependent retriever tests also run outside the `integration` marker.

The Makefile provides `make run`, `make test`, and `make lint` as shortcuts. `make format` runs the formatter and applies Ruff fixes.

Run the agent and retriever directly with the debug scripts.

```bash
uv run python scripts/check_agent.py
uv run python scripts/check_retriever.py "study duration"
```

## Configuration

Copy [`.env.example`](.env.example) for the starting configuration.

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLM_API_KEY` | Required | API key for the configured LLM provider |
| `LLM_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta/openai/` | OpenAI-compatible endpoint for the LLM |
| `LLM_MODEL` | `gemini-2.5-flash` | Model name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant endpoint. Compose sets it to `http://qdrant:6333` for the app. |
| `QDRANT_COLLECTION` | `documents` | Qdrant collection for indexed document chunks |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Local fastembed model. The Qdrant collection expects 384-dimensional vectors. |

For local runs with another OpenAI-compatible provider, set `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` in `.env`. For Compose, also pass `LLM_BASE_URL` into the app container through its environment.

## Troubleshooting

- For Gemini's `429 RESOURCE_EXHAUSTED`, check your provider quota or retry after the rate-limit window.
- If Python cannot import `src`, run `uv sync` from the repository root to install the project in editable mode.
- If the client raises `httpcore.UnsupportedProtocol`, check that `LLM_BASE_URL`, when set, is a complete URL.
- If a local app cannot reach Qdrant, start it with `docker compose up -d qdrant` and check `QDRANT_URL`.

## Architecture

- The app implements the ReAct loop directly and exposes registered tools to the model. The prompt describes when document search is appropriate.
- `LLMProvider` defines the client interface. The default implementation uses the OpenAI SDK.
- fastembed computes embeddings locally once the model is available. Qdrant stores and searches the vectors.
- Public HTTP schemas live in `src/schemas/`. Agent and retrieval models live in their respective packages.
