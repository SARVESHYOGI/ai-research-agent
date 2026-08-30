import asyncio

import psycopg
from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.redis import AsyncRedisDep
from app.core.redis_health import redis_health_check

router = APIRouter(prefix="/health", tags=["health"])


class ServiceCheck(BaseModel):
    name: str
    status: str
    detail: str | None = None
    latency_ms: float | None = None


async def check_database(database_url: str, timeout: float) -> ServiceCheck:
    started = asyncio.get_event_loop().time()
    try:
        await asyncio.wait_for(
            asyncio.to_thread(_ping_database, database_url, timeout),
            timeout=timeout,
        )
    except Exception as exc:
        return ServiceCheck(
            name="database",
            status="unhealthy",
            detail=_db_error_detail(exc),
            latency_ms=_elapsed_ms(started),
        )
    return ServiceCheck(
        name="database",
        status="healthy",
        latency_ms=_elapsed_ms(started),
    )


def _db_error_detail(exc: Exception) -> str:
    if isinstance(exc, asyncio.TimeoutError):
        return "connection timed out"
    return str(exc)


def _ping_database(database_url: str, timeout: float) -> None:
    connect_timeout = max(1, int(timeout))
    with (
        psycopg.connect(database_url, connect_timeout=connect_timeout) as conn,
        conn.cursor() as cur,
    ):
        cur.execute("SELECT 1")


def _elapsed_ms(started: float) -> float:
    return round((asyncio.get_event_loop().time() - started) * 1000, 2)


async def _redis_check(client) -> ServiceCheck:
    result = await redis_health_check(client)
    return ServiceCheck(
        name="redis",
        status=result.status.value,
        detail=result.detail,
        latency_ms=result.latency_ms,
    )


@router.get("", status_code=status.HTTP_200_OK)
async def health_check(redis: AsyncRedisDep):
    from app.config.settings import get_settings

    settings = get_settings()
    checks: dict[str, ServiceCheck] = {"redis": await _redis_check(redis)}
    if settings.database_url:
        checks["database"] = await check_database(
            settings.database_url, settings.database_check_timeout
        )
    overall = "healthy" if all(c.status == "healthy" for c in checks.values()) else "unhealthy"
    return {
        "status": overall,
        "checks": {name: c.model_dump() for name, c in checks.items()},
    }
