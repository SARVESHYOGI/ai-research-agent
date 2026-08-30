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
    redis = FastAPIRedis(app).lifespan()
    if caching:
        redis = redis.caching()
    if rate_limiting:
        redis = redis.rate_limiting()
    if otel:
        redis = redis.otel()
    return redis
