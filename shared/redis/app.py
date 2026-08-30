"""Idiomatic Redis wiring for FastAPI apps.

Builds on the official ``fastapi-redis-sdk``: a single shared async connection
pool managed through the FastAPI lifespan, with opt-in DI caching, rate limiting
and OpenTelemetry. The builder wraps any existing lifespan rather than replacing
it, so multiple libraries can each register their own startup/shutdown logic.
"""

from __future__ import annotations

from fastapi import FastAPI
from redis_fastapi import FastAPIRedis


def setup_redis(
    app: FastAPI,
    *,
    caching: bool = True,
    rate_limiting: bool = True,
    otel: bool = False,
) -> FastAPIRedis:
    """Attach the shared Redis connection pool (and optional features) to ``app``.

    The lifespan-managed connection pool is opened at startup and drained
    gracefully on shutdown. ``caching`` enables the ``cache()`` /
    ``cache_evict()`` / ``cache_put()`` dependency factories, and
    ``rate_limiting`` enables the ``rate_limit()`` factory.

    All connection settings come from environment variables prefixed with
    ``REDIS_`` (see ``fastapi-redis-sdk`` configuration), most simply::

        REDIS_URL=redis://localhost:6379/0

    Returns the builder instance for chaining or inspection.
    """
    redis = FastAPIRedis(app).lifespan()
    if caching:
        redis = redis.caching()
    if rate_limiting:
        redis = redis.rate_limiting()
    if otel:
        redis = redis.otel()
    return redis
