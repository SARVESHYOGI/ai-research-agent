.PHONY: install run test lint format

PYTHON ?= uv run

install:
	uv sync

run:
	$(PYTHON) uvicorn app.main:app --reload

test:
	$(PYTHON) pytest

lint:
	$(PYTHON) ruff check .

format:
	$(PYTHON) ruff format .
