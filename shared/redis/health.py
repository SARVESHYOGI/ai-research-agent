"""Redis health checks that reuse the SDK-managed connection pool.

The client is obtained with :data:`shared.redis.AsyncRedisDep` so the check
reuses the single lifespan-managed pool instead of opening its own connection.
"""

from __future__ import annotations

import asyncio
from enum import StrEnum

from pydantic import BaseModel


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class RedisHealth(BaseModel):
    name: str = "redis"
    status: HealthStatus
    detail: str | None = None
    latency_ms: float | None = None


async def redis_health_check(client) -> RedisHealth:
    """Ping the given ``client`` and report its health.

    ``client`` is expected to come from ``AsyncRedisDep`` (the shared
    lifespan-managed pool). Any non-recoverable failure is reported as
    ``unhealthy``; a failed ping is ``unhealthy``.
    """
    started = asyncio.get_event_loop().time()
    try:
        await client.ping()
    except Exception as exc:
        return RedisHealth(
            status=HealthStatus.UNHEALTHY,
            detail=str(exc),
            latency_ms=_elapsed_ms(started),
        )
    return RedisHealth(status=HealthStatus.HEALTHY, latency_ms=_elapsed_ms(started))


def _elapsed_ms(started: float) -> float:
    return round((asyncio.get_event_loop().time() - started) * 1000, 2)
