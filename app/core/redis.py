"""Cache, rate limiting and Redis client wiring for the monolith.

Reuses the official ``fastapi-redis-sdk`` on its own (no service split), so the
whole app shares a single async connection pool through the FastAPI lifespan.
"""

from __future__ import annotations

from fastapi import FastAPI
from redis_fastapi import (
    AsyncRedisDep,
    CacheBackendDep,
    FastAPIRedis,
    cache,
    cache_evict,
    cache_put,
    rate_limit,
)

from app.core.redis_health import HealthStatus, redis_health_check

__all__ = [
    "setup_redis",
    "AsyncRedisDep",
    "CacheBackendDep",
    "cache",
    "cache_evict",
    "cache_put",
    "rate_limit",
    "redis_health_check",
    "HealthStatus",
]


def setup_redis(
    app: FastAPI,
    *,
    caching: bool = True,
    rate_limiting: bool = True,
    otel: bool = False,
) -> FastAPIRedis:
    """Attach the shared Redis connection pool (and optional features) to ``app``.

    The lifespan-managed connection pool is opened at startup and drained
    gracefully on shutdown. Connection settings come from environment variables
    prefixed with ``REDIS_``, most simply::

        REDIS_URL=redis://localhost:6379/0
    """
    redis = FastAPIRedis(app).lifespan()
    if caching:
        redis = redis.caching()
    if rate_limiting:
        redis = redis.rate_limiting()
    if otel:
        redis = redis.otel()
    return redis
