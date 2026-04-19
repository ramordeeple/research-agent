.PHONY: run lint format test

run:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

test:
	uv run pytest -v