"""Shared FastAPI + Redis foundation.

Wraps the official ``fastapi-redis-sdk`` so every service configures Redis the
same way, from a single stable API. The SDK manages a shared async connection
pool through the FastAPI lifespan and exposes dependency-injection caching and
rate limiting.
"""

from shared.redis.app import setup_redis
from shared.redis.deps import (
    AsyncRedisDep,
    CacheBackendDep,
    cache,
    cache_evict,
    cache_put,
    rate_limit,
)
from shared.redis.health import HealthStatus, redis_health_check

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
