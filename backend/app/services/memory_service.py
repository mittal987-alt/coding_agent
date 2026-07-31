from __future__ import annotations

from typing import Any

from app.config.settings import Settings
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
)
from app.services.base import BaseService
class MemoryService(BaseService):
    """
    Handles conversation history,
    semantic memory,
    vector search,
    and long-term knowledge.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        container: Any,
    ) -> None:

        super().__init__(
            settings=settings,
            container=container,
        )
            @property
    def manager(self):
        return self.resolve("memory_manager")


    @property
    def vector_store(self):
        return self.resolve("vector_store")


    @property
    def llm(self):
        return self.resolve("llm_manager")
        async def create_session(
        self,
        session_id: str,
    ):

        return await self.manager.create_session(
            session_id,
        )
        async def load(
        self,
        session_id: str,
    ):

        history = await self.manager.load(
            session_id,
        )

        if history is None:
            raise NotFoundError(
                "Conversation not found."
            )

        return history
        async def append(
        self,
        *,
        session_id: str,
        user_message: str,
        assistant_message: str,
    ):

        return await self.manager.append(

            session_id=session_id,

            user_message=user_message,

            assistant_message=assistant_message,
        )
        async def store(
        self,
        *,
        session_id: str,
        content: str,
        metadata: dict | None = None,
    ):

        embedding = await self.llm.embedding(
            content,
        )

        return await self.vector_store.add(

            text=content,

            embedding=embedding,

            metadata=metadata or {
                "session": session_id,
            },
        )
    async def search(
        self,
        query: str,
        limit: int = 5,
    ):

        embedding = await self.llm.embedding(
            query,
        )

        return await self.vector_store.search(

            embedding=embedding,

            limit=limit,
        )
    async def summarize(
        self,
        session_id: str,
    ):

        history = await self.load(
            session_id,
        )

        return await self.llm.summarize(
            history,
        )
    async def delete(
        self,
        session_id: str,
    ):

        return await self.manager.delete(
            session_id,
        )
    async def clear(
        self,
        session_id: str,
    ):

        return await self.manager.clear(
            session_id,
        )
    async def sessions(self):

        return await self.manager.sessions()
    async def context(
        self,
        query: str,
        limit: int = 8,
    ):

        memories = await self.search(
            query=query,
            limit=limit,
        )

        return "\n".join(
            item.text
            for item in memories
        )
    async def update_metadata(
        self,
        *,
        memory_id: str,
        metadata: dict,
    ):

        return await self.vector_store.update_metadata(

            memory_id,

            metadata,
        )
    async def delete_memory(
        self,
        memory_id: str,
    ):

        return await self.vector_store.delete(
            memory_id,
        )
    async def rebuild_embeddings(self):

        memories = await self.vector_store.all()

        for memory in memories:

            embedding = await self.llm.embedding(
                memory.text,
            )

            await self.vector_store.update_embedding(

                memory.id,

                embedding,
            )

        return True
    async def statistics(self):

        return await self.vector_store.statistics() 
    async def health_check(self):

        return {

            "service": "MemoryService",

            "healthy": True,

            "vector_store": True,

            "memory_manager": True,

            "embedding": True,
        }   