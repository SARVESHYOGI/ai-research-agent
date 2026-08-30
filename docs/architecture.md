# AI Research Agent — Architecture

## Decision: Monolith (not microservices)

This project was originally planned as a distributed, event-driven
microservices platform (separate `agent-service`, `memory-service`,
`research-service`, `career-service`, `llm-gateway`, `tool-gateway`, a Redis
message broker, and per-service PostgreSQL schemas).

That architecture was **removed** in favour of a **monolithic FastAPI
application** for the following reasons:

- The codebase was almost entirely empty scaffolding (0-byte stubs) — no real
  per-service behaviour existed to justify the distributed overhead.
- A monolith is far simpler to develop, test, debug and deploy.
- The distributed concerns (service isolation, independent scaling, message
  broker) can be reintroduced later only if the workload genuinely requires
  them (see "Future evolution").

## Package layout

All domain code lives in one package, `app/`, subdivided by feature so the
code stays organised:

| Path | Responsibility |
| --- | --- |
| `app/main.py` | Single FastAPI app, lifespan, Redis setup, routers, middleware |
| `app/config/` | Settings (pydantic-settings, `AI_RESEARCH_` env prefix) |
| `app/core/` | Shared infra: Redis client, cache, rate limiting, health |
| `app/api/` | Versioned routers (`/v1/...`) — HTTP boundary |
| `app/agent/` | Planner, state machine, executor, recovery, checkpointing |
| `app/memory/` | Structured/semantic/episodic/procedural memory + retrieval |
| `app/research/` | Search, fetch, extraction, chunking, verification, synthesis |
| `app/career/` | Job matching, resume, skills, company analysis |
| `app/llm/` | LLM provider abstraction + cost/token tracking |
| `app/tools/` | Typed tools (web_search, web_fetch, pdf_reader, ...) |
| `app/models/` | SQLAlchemy models |
| `app/services/` | Business orchestration (task service, ...) |

## Key design points

- **One process, one app.** The FastAPI application in `app/main.py` composes
  every feature. No service-to-service HTTP calls, no direct shared-DB writes
  across boundaries; modules call each other directly.
- **Redis** is used for caching and rate limiting only (via the single shared
  async connection pool in `app/core/redis.py`), not as a message broker.
- **Async work** is handled in-process (e.g. FastAPI `BackgroundTasks`, or a
  task queue such as Celery/ARQ built on the same Redis), rather than through
  distributed workers.

## Database

One PostgreSQL database owned by the application. Schema changes are managed
with Alembic migrations (under `migrations/`). The per-service logical schemas
from the distributed design were removed in favour of a single ownership model.

## Configuration

Settings are loaded through `app/config/settings.py` from environment variables
prefixed with `AI_RESEARCH_` plus a `.env` file. See the root `.env.example`.

## Future evolution

The monolith can be split into separate deployable units *if* needed, guided by
the original requirements in `prd.md`. The feature folders under `app/` are
already aligned with the natural service boundaries, which keeps such a split
feasible later without a ground-up rewrite.
