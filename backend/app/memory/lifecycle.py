# lifecycle.py
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from .manager import BaseMemoryStore
from .models import (
    MemoryDocument,
    MemoryStatus,
)

logger = logging.getLogger(__name__)


class MemoryLifecycleManager:
    """
    Manages the lifecycle of memories.

    Features:
    - Expiration
    - Importance decay
    - Promotion
    - Archival
    - Cleanup
    """

    def __init__(
        self,
        store: BaseMemoryStore,
        *,
        archive_after_days: int = 180,
        delete_after_days: int = 365,
        decay_rate: float = 0.02,
        promotion_threshold: int = 20,
    ) -> None:

        self.store = store

        self.archive_after = archive_after_days
        self.delete_after = delete_after_days
        self.decay_rate = decay_rate
        self.promotion_threshold = promotion_threshold

    async def process(
        self,
        documents: list[MemoryDocument],
    ) -> None:
        """
        Run lifecycle management on all memories.
        """

        now = datetime.utcnow()

        for document in documents:

            changed = False

            age_days = (
                now - document.updated_at
            ).days

            # --------------------------------
            # Expiration
            # --------------------------------

            if (
                document.expires_at
                and document.expires_at <= now
            ):

                document.status = MemoryStatus.DELETED

                changed = True

            # --------------------------------
            # Archive
            # --------------------------------

            elif (
                age_days >= self.archive_after
                and document.status
                == MemoryStatus.ACTIVE
            ):

                document.status = MemoryStatus.ARCHIVED

                changed = True

            # --------------------------------
            # Importance decay
            # --------------------------------

            document.importance = max(
                0.1,
                document.importance
                - self.decay_rate,
            )

            # --------------------------------
            # Promotion
            # --------------------------------

            if (
                document.access_count
                >= self.promotion_threshold
            ):

                document.importance = min(
                    1.0,
                    document.importance + 0.15,
                )

            if changed:

                await self.store.update(
                    document
                )

    async def cleanup(
        self,
        documents: list[MemoryDocument],
    ) -> int:
        """
        Permanently remove obsolete memories.
        """

        now = datetime.utcnow()

        removed = 0

        for document in documents:

            age = (
                now - document.updated_at
            ).days

            if (
                document.status
                == MemoryStatus.DELETED
                and age >= self.delete_after
            ):

                await self.store.delete(
                    document.id
                )

                removed += 1

        logger.info(
            "Lifecycle cleanup removed %d memories.",
            removed,
        )

        return removed

    async def promote(
        self,
        document: MemoryDocument,
    ) -> MemoryDocument:
        """
        Promote a memory because it is frequently used.
        """

        document.importance = min(
            1.0,
            document.importance + 0.25,
        )

        document.updated_at = datetime.utcnow()

        await self.store.update(document)

        return document

    async def archive(
        self,
        document: MemoryDocument,
    ) -> MemoryDocument:

        document.status = MemoryStatus.ARCHIVED

        await self.store.update(
            document
        )

        return document

    async def restore(
        self,
        document: MemoryDocument,
    ) -> MemoryDocument:

        document.status = MemoryStatus.ACTIVE

        await self.store.update(
            document
        )

        return document

    async def touch(
        self,
        document: MemoryDocument,
    ) -> None:
        """
        Update access information.
        """

        document.access_count += 1

        document.last_accessed_at = datetime.utcnow()

        await self.store.update(
            document
        )

    def statistics(
        self,
        documents: list[MemoryDocument],
    ) -> dict:

        active = 0
        archived = 0
        deleted = 0

        for document in documents:

            if (
                document.status
                == MemoryStatus.ACTIVE
            ):
                active += 1

            elif (
                document.status
                == MemoryStatus.ARCHIVED
            ):
                archived += 1

            else:
                deleted += 1

        return {
            "total": len(documents),
            "active": active,
            "archived": archived,
            "deleted": deleted,
        }