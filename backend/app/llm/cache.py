# LLM Cache
from __future__ import annotations

import asyncio
import hashlib
import json
from collections import OrderedDict
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field

from .provider import ChatRequest, ChatResponse


# ============================================================
# Models
# ============================================================


class CacheEntry(BaseModel):
    """
    Cached LLM response.
    """

    key: str

    response: ChatResponse

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    expires_at: datetime

    hits: int = 0


class CacheStatistics(BaseModel):
    """
    Cache metrics.
    """

    entries: int = 0

    hits: int = 0

    misses: int = 0

    evictions: int = 0

    expirations: int = 0

    hit_rate: float = 0.0


# ============================================================
# Cache
# ============================================================


class LLMCache:
    """
    Thread-safe in-memory LRU cache.

    Future implementations:
    - Redis
    - Memcached
    - SQLite
    """

    def __init__(
        self,
        *,
        max_size: int = 1000,
        ttl_seconds: int = 3600,
    ) -> None:

        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)

        self._cache: OrderedDict[
            str,
            CacheEntry,
        ] = OrderedDict()

        self._lock = asyncio.Lock()

        self._stats = CacheStatistics()

    # ---------------------------------------------------------
    # Key Generation
    # ---------------------------------------------------------

    def make_key(
        self,
        request: ChatRequest,
    ) -> str:
        """
        Generate a deterministic cache key.
        """

        payload = {
            "model": request.model,
            "messages": [
                message.model_dump(mode="json")
                for message in request.messages
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "tools": [
                tool.model_dump(mode="json")
                for tool in request.tools
            ],
        }

        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    # ---------------------------------------------------------
    # CRUD
    # ---------------------------------------------------------

    async def get(
        self,
        request: ChatRequest,
    ) -> ChatResponse | None:

        key = self.make_key(request)

        async with self._lock:

            entry = self._cache.get(key)

            if entry is None:
                self._stats.misses += 1
                return None

            if entry.expires_at < datetime.now(UTC):

                del self._cache[key]

                self._stats.expirations += 1
                self._stats.misses += 1

                return None

            entry.hits += 1

            self._stats.hits += 1

            self._cache.move_to_end(key)

            return entry.response

    async def set(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> None:

        key = self.make_key(request)

        async with self._lock:

            if key in self._cache:
                self._cache.move_to_end(key)

            self._cache[key] = CacheEntry(
                key=key,
                response=response,
                expires_at=datetime.now(UTC)
                + self.ttl,
            )

            while len(self._cache) > self.max_size:

                self._cache.popitem(last=False)

                self._stats.evictions += 1

    async def delete(
        self,
        request: ChatRequest,
    ) -> bool:

        key = self.make_key(request)

        async with self._lock:

            return self._cache.pop(
                key,
                None,
            ) is not None

    async def clear(
        self,
    ) -> None:

        async with self._lock:

            self._cache.clear()

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    async def contains(
        self,
        request: ChatRequest,
    ) -> bool:

        return (
            await self.get(request)
            is not None
        )

    async def cleanup(
        self,
    ) -> None:

        now = datetime.now(UTC)

        async with self._lock:

            expired = [
                key
                for key, entry in self._cache.items()
                if entry.expires_at < now
            ]

            for key in expired:
                del self._cache[key]

            self._stats.expirations += len(expired)

    async def statistics(
        self,
    ) -> CacheStatistics:

        total = (
            self._stats.hits
            + self._stats.misses
        )

        self._stats.entries = len(self._cache)

        self._stats.hit_rate = (
            self._stats.hits / total
            if total
            else 0.0
        )

        return self._stats