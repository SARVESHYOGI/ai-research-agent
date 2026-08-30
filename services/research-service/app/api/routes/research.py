import asyncio

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from shared.redis import AsyncRedisDep, cache, redis_health_check

router = APIRouter(prefix="/v1", tags=["research"])


class SearchResult(BaseModel):
    query: str
    hits: int


class Health(BaseModel):
    status: str
    checks: dict


@router.get("/health", status_code=status.HTTP_200_OK)
async def health(redis: AsyncRedisDep):
    result = await redis_health_check(redis)
    healthy = result.status.value == "healthy"
    return Health(status="healthy" if healthy else "unhealthy", checks={"redis": result.model_dump()})


@router.get("/search", response_model=SearchResult)
async def search(query: str, _: None = Depends(cache(ttl=60, eviction_group="search"))):
    await asyncio.sleep(0.1)
    return SearchResult(query=query, hits=len(query.split()))
