# AI Research Agent

Memory-aware autonomous research agent — a **monolithic FastAPI application**.

## Architecture

Single-process, service-oriented-in-package layout. All domain logic lives
under one `app/` package and communicates through direct function calls (no
distributed message broker, no per-service network calls).

```
app/
├── main.py            # one FastAPI app (create_app)
├── config/            # settings (env-config, pydantic-settings)
├── core/              # shared infra: Redis client, cache, rate limiting
├── api/               # versioned routers (health, research, ...)
├── agent/             # (planned) planner, state machine, executor
├── memory/            # (planned) four memory types + retrieval
├── research/          # (planned) search, fetch, extraction, verification
├── career/            # (planned) matching, resume, skills
├── llm/               # (planned) providers + cost/token tracking
├── tools/             # (planned) web_search, web_fetch, pdf_reader
├── models/            # (planned) SQLAlchemy models
└── services/          # (planned) business orchestration
```

## Getting started

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                # install deps into .venv
uv run uvicorn app.main:app --reload   # or: make run
```

Redis is used for caching and rate limiting. Start it with:

```bash
docker compose up redis
```

Open the interactive API docs at http://localhost:8000/docs.

## Configuration

See [`.env.example`](.env.example). Key variables:

| Variable | Purpose |
| --- | --- |
| `REDIS_URL` | Redis connection string (caching + rate limiting) |
| `AI_RESEARCH_DATABASE_URL` | PostgreSQL URL (optional, for health check) |

## Tests

```bash
uv run pytest          # or: make test
```

Redis-dependent tests are skipped unless a Redis is running and
`TEST_REDIS=1` (default) is set. To run without Redis: `TEST_REDIS=0 uv run pytest`.

## Lint & format

```bash
make lint              # ruff check
make format            # ruff format
```

## Building the project end to end

See [`steps.md`](steps.md) for a detailed, ordered build path from the current
skeleton to a fully working agent (data layer, LLM, research, memory, agent
harness, security, career, observability, frontend, evaluation, deploy). Every
phase ends with a verifiable "Done when" gate.

## Project history / status

This codebase was previously scaffolded as a distributed, event-driven
microservices platform (separate `services/`, `shared/` packages, Redis message
broker, per-service schemas). It was restructured into a **monolith** before
significant implementation. `prd.md` contains the product requirements and the
original (now superseded) distributed design; `checklist.html` tracks the build
checklist.
