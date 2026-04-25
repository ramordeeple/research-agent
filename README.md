# AI Research Agent

AI-агент с поддержкой RAG (Retrieval-Augmented Generation) и ReAct reasoning loop для исследовательских задач. Принимает документы (PDF / TXT / Markdown), индексирует их в векторной БД и отвечает на вопросы, используя инструменты и контекст из загруженных материалов.

## Возможности

**Реализовано:**
- **RAG** — загрузка документов в форматах PDF, TXT, Markdown с автоматическим чанкингом и эмбеддингом
- **Векторный поиск** через Qdrant с локальными эмбеддингами (BGE-small-en-v1.5)
- **ReAct агент** — собственная реализация цикла Thought → Action → Observation без LangChain
- **Tools** — `calculator` (безопасный AST-парсер) и `rag_search` (поиск по загруженным документам)
- **HTTP API** на FastAPI с эндпоинтами `/chat`, `/ingest`, `/health`
- **Provider-independent LLM** — работает через OpenAI-совместимый API (по умолчанию Gemini)
- **Docker-окружение** — multi-stage сборка, non-root user, предзагруженная модель эмбеддингов

## Стек

- Python 3.12
- FastAPI + uvicorn
- Pydantic v2 / pydantic-settings
- Qdrant (векторная БД)
- fastembed (BGE-small-en-v1.5, 384 dim)
- OpenAI SDK (используется через OpenAI-совместимый endpoint Gemini)
- pypdf для парсинга PDF
- pytest + pytest-asyncio + ruff
- Docker + Docker Compose
- uv (менеджер пакетов)

## Требования

Для запуска нужны:
- **Docker** и **Docker Compose** 
- **API ключ Gemini** — бесплатно на [aistudio.google.com](https://aistudio.google.com)

## Быстрый старт (Docker)

Это рекомендуемый способ запуска.

### 1. Получи API ключ
В проекте использовался [aistudio.google.com](https://aistudio.google.com)

### 2. Склонируй репозиторий и подготовь .env



Открой `.env` и впиши свой ключ:

```
LLM_API_KEY=<YOUR_API_KEY>
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL=gemini-2.5-flash
LOG_LEVEL=INFO
QDRANT_URL=http://localhost:6333
```

### 3. Запусти через Docker Compose

```bash
docker compose up
```

После старта приложение доступно на:
- **Swagger UI**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1/

### 4. Проверь работу

Через Swagger UI:
1. Открой http://localhost:8000/docs
2. Зайди в `POST /api/v1/ingest` → "Try it out" → загрузи PDF/TXT/MD файл
3. Зайди в `POST /api/v1/chat` → задай вопрос по документу

## API

### `GET /api/v1/health`

Проверка живости сервиса.

**Ответ:**
```json
{"status": "ok"}
```

### `POST /api/v1/ingest`

Загрузка документа в векторную БД. Принимает multipart/form-data.

**Поддерживаемые форматы:** `.pdf`, `.txt`, `.md`

**Запрос:**
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@document.pdf"
```

**Ответ:**
```json
{
  "filename": "document.pdf",
  "chunks_added": 42
}
```

### `POST /api/v1/chat`

Вопрос агенту. Агент сам решает, использовать ли инструменты (RAG-поиск, калькулятор) на основе вопроса.

**Запрос:**
```json
{
  "message": "Сколько будет 234 * 567?"
}
```

**Ответ:**
```json
{
  "answer": "234 * 567 = 132678",
  "sources": []
}
```

Для вопросов по загруженным документам:
```json
{
  "message": "Что говорится в книге про указатели?"
}
```

**Ответ:**
```json
{
  "answer": "Согласно загруженным материалам, указатели...",
  "sources": [
    {"filename": "book.pdf", "score": 0.87},
    {"filename": "book.pdf", "score": 0.81}
  ]
}
```



## Разработка

### Команды Makefile

```bash
make run          # запуск dev-сервера с reload
make test         # все тесты
make lint         # ruff check
make format       # ruff format + auto-fix
```

### Тесты

```bash
uv run pytest -v
```

Часть тестов помечена `@pytest.mark.integration` — они требуют запущенный Qdrant и валидный `LLM_API_KEY`. Юнит-тесты работают без этого.

### Скрипты для отладки

В папке `scripts/` лежат ручные утилиты:

```bash
uv run python scripts/check_chat.py "тестовый вопрос"
uv run python scripts/check_agent.py "вопрос для агента"
uv run python scripts/check_retriever.py "что искать"
```

## Конфигурация

Все настройки через переменные окружения (см. `.env.example`):

| Переменная | По умолчанию | Описание |
|---|---|---|
| `LLM_API_KEY` | — (обязательно) | Ключ от LLM провайдера |
| `LLM_BASE_URL` | Gemini OpenAI-compat endpoint | Можно поменять на OpenAI/Groq/любой OpenAI-совместимый |
| `LLM_MODEL` | `gemini-2.5-flash` | Имя модели |
| `LOG_LEVEL` | `INFO` | `DEBUG`/`INFO`/`WARNING`/`ERROR` |
| `QDRANT_URL` | `http://localhost:6333` | URL Qdrant (в Docker Compose: `http://qdrant:6333`) |
| `QDRANT_COLLECTION` | `documents` | Имя коллекции в Qdrant |

## Возможные проблемы

**`429 RESOURCE_EXHAUSTED` от Gemini** — превышен лимит бесплатного tier. Подожди минуту или смени модель на менее загруженную.

**`ModuleNotFoundError: No module named 'src'`** при тестах — выполни `uv sync`, чтобы пакет установился в editable-режиме.

**Контейнер падает с `httpcore.UnsupportedProtocol`** — проверь что в `.env` задан `LLM_BASE_URL`. Пустое значение перетирает дефолт.

**Qdrant connection refused при локальном запуске** — убедись что Qdrant поднят отдельно: `docker compose up qdrant`.

## Архитектурные решения

Несколько ключевых решений и почему так:

**Без LangChain.** ReAct реализован вручную — для прозрачности, отсутствия breaking changes и понимания происходящего внутри.

**Provider-independent LLM.** Через `LLMProvider(Protocol)` + OpenAI-совместимый endpoint. Чтобы сменить Gemini на OpenAI/Groq — достаточно поменять две переменные в `.env`, код не трогается.

**Локальные эмбеддинги вместо API.** fastembed работает офлайн, нет лимитов, не требует ключей и одинаково ведёт себя в dev и prod.

**Два слоя схем.** `src/schemas/` для публичного API (контракт с клиентом), `src/<module>/schemas.py` для внутренних доменных моделей. Не смешиваются, чтобы изменения внутри не ломали API.

**Безопасность tools через whitelist.** Никаких `python_exec`/`shell`. Калькулятор использует AST-парсер вместо `eval()`. Системный промпт явно ограничивает scope агента.