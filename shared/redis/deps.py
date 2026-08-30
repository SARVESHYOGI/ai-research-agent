"""Re-export the SDK's dependency-injection primitives.

Services import from :mod:`shared.redis` instead of the SDK package directly so
that swapping the underlying Redis integration later does not touch service
code.
"""

from redis_fastapi import (
    AsyncRedisDep,
    CacheBackendDep,
    cache,
    cache_evict,
    cache_put,
    rate_limit,
)

__all__ = [
    "AsyncRedisDep",
    "CacheBackendDep",
    "cache",
    "cache_evict",
    "cache_put",
    "rate_limit",
]
