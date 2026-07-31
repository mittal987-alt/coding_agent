# cache.py
from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class CacheEntry(Generic[T]):
    value: T
    expires_at: float | None


@dataclass(slots=True)
class CacheStatistics:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0

    @property
    def requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.requests == 0:
            return 0.0

        return self.hits / self.requests


class MemoryCache:
    """
    Async thread-safe LRU cache.

    Features

    - TTL
    - LRU eviction
    - Statistics
    """

    def __init__(
        self,
        max_size: int = 1024,
        default_ttl: int = 3600,
    ) -> None:

        self.max_size = max_size
        self.default_ttl = default_ttl

        self._cache: OrderedDict[
            str,
            CacheEntry,
        ] = OrderedDict()

        self._lock = asyncio.Lock()

        self._stats = CacheStatistics()

    async def get(
        self,
        key: str,
    ):

        async with self._lock:

            if key not in self._cache:

                self._stats.misses += 1

                return None

            entry = self._cache[key]

            if (
                entry.expires_at is not None
                and entry.expires_at < time.time()
            ):

                del self._cache[key]

                self._stats.expirations += 1
                self._stats.misses += 1

                return None

            self._cache.move_to_end(key)

            self._stats.hits += 1

            return entry.value

    async def set(
        self,
        key: str,
        value,
        ttl: int | None = None,
    ) -> None:

        async with self._lock:

            if key in self._cache:

                del self._cache[key]

            expires_at = None

            if ttl is None:

                ttl = self.default_ttl

            if ttl > 0:

                expires_at = time.time() + ttl

            self._cache[key] = CacheEntry(
                value=value,
                expires_at=expires_at,
            )

            self._cache.move_to_end(key)

            while len(self._cache) > self.max_size:

                self._cache.popitem(last=False)

                self._stats.evictions += 1

    async def delete(
        self,
        key: str,
    ) -> bool:

        async with self._lock:

            if key not in self._cache:

                return False

            del self._cache[key]

            return True

    async def clear(self) -> None:

        async with self._lock:

            self._cache.clear()

    async def contains(
        self,
        key: str,
    ) -> bool:

        return await self.get(key) is not None

    async def size(self) -> int:

        async with self._lock:

            return len(self._cache)

    async def keys(self) -> list[str]:

        async with self._lock:

            return list(self._cache.keys())

    def stats(self) -> CacheStatistics:

        return self._stats