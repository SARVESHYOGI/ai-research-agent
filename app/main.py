"""AI Research Agent — monolithic FastAPI application.

A single-process, single-package application. All domain modules (agent,
memory, research, career, llm, tools) live under this same ``app`` package and
communicate through direct calls rather than a distributed message broker.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.api import health, research
from app.config.settings import get_settings
from app.core.redis import AsyncRedisDep, cache, rate_limit, setup_redis

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("startup", app=settings.app_name, version=settings.version)
        yield
        logger.info("shutdown")

    app = FastAPI(
        title=settings.app_name,
        description="Memory-aware autonomous research agent (monolith).",
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    setup_redis(app=app, caching=True, rate_limiting=True)

    app.include_router(health.router, prefix="/v1")
    app.include_router(research.router)

    @app.get("/")
    def read_root():
        return {"service": settings.app_name}

    @app.get("/v1/redis/ping")
    async def redis_ping(redis: AsyncRedisDep):
        await redis.ping()
        return {"status": "ok"}

    @app.get(
        "/v1/cache-demo",
        dependencies=[Depends(cache(ttl=30, eviction_group="cache-demo"))],
    )
    async def cache_demo():
        return {"value": time.time()}

    @app.get("/v1/rate-demo", dependencies=[Depends(rate_limit("3/minute"))])
    async def rate_demo():
        return {"status": "ok"}

    @app.middleware("http")
    async def log_requests(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        response.headers["X-Response-Time"] = f"{(time.time() - start_time) * 1000:.2f}ms"
        return response

    return app


app = create_app()
