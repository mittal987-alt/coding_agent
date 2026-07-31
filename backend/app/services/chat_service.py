from __future__ import annotations

from typing import Any, AsyncGenerator

from app.config.settings import Settings
from app.services.base import BaseService
from app.core.exceptions import (
    ValidationError,
)
class ChatService(BaseService):
    """
    Orchestrates conversations between the user,
    LLM providers, memory, and tools.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        container: Any,
    ):

        super().__init__(
            settings=settings,
            container=container,
        )
    @property
    def llm(self):
        return self.resolve("llm_manager")


    @property
    def memory(self):
        return self.resolve("memory_manager")


    @property
    def workspace(self):
        return self.resolve("workspace_manager")


    @property
    def tools(self):
        return self.resolve("tool_registry")


    @property
    def planner(self):
        return self.resolve("planner")
    async def chat(
        self,
        *,
        session_id: str,
        message: str,
        model: str | None = None,
        metadata: dict | None = None,
    ):

        if not message.strip():
            raise ValidationError(
                "Message cannot be empty."
            )

        history = await self.memory.load(
            session_id,
        )

        response = await self.llm.chat(

            message=message,

            history=history,

            model=model,

            metadata=metadata or {},
        )

        await self.memory.append(

            session_id=session_id,

            user_message=message,

            assistant_message=response.content,
        )

        await self.publish(
            "chat.completed",
            {
                "session": session_id,
            },
        )

        return response
    async def stream_chat(
        self,
        *,
        session_id: str,
        message: str,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:

        history = await self.memory.load(
            session_id,
        )

        full_response = ""

        async for chunk in self.llm.stream(

            message=message,

            history=history,

            model=model,
        ):

            full_response += chunk

            yield chunk

        await self.memory.append(

            session_id=session_id,

            user_message=message,

            assistant_message=full_response,
        )
    async def stream_chat(
        self,
        *,
        session_id: str,
        message: str,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:

        history = await self.memory.load(
            session_id,
        )

        full_response = ""

        async for chunk in self.llm.stream(

            message=message,

            history=history,

            model=model,
        ):

            full_response += chunk

            yield chunk

        await self.memory.append(

            session_id=session_id,

            user_message=message,

            assistant_message=full_response,
        )
    async def chat_with_tools(
        self,
        *,
        session_id: str,
        message: str,
        workspace: str,
        model: str | None = None,
    ):

        history = await self.memory.load(
            session_id,
        )

        response = await self.llm.chat(

            message=message,

            history=history,

            model=model,

            enable_tools=True,
        )

        if not response.tool_calls:
            return response

        tool_results = []

        for call in response.tool_calls:

            result = await self.tools.execute(

                tool=call.name,

                arguments=call.arguments,

                workspace=workspace,
            )

            tool_results.append(result)

        final = await self.llm.chat(

            message=message,

            history=history,

            tool_results=tool_results,

            model=model,
        )

        return final
    async def summarize(
        self,
        session_id: str,
    ):

        history = await self.memory.load(
            session_id,
        )

        return await self.llm.summarize(
            history,
        )
    async def search_memory(
        self,
        query: str,
        limit: int = 5,
    ):

        return await self.memory.search(
            query,
            limit,
        )
    async def reset(
        self,
        session_id: str,
    ):

        await self.memory.clear(
            session_id,
        )

        return True
    async def history(
        self,
        session_id: str,
    ):

        return await self.memory.load(
            session_id,
        )
    async def sessions(self):

        return await self.memory.sessions()
    async def estimate_tokens(
        self,
        text: str,
        model: str | None = None,
    ):

        return await self.llm.estimate_tokens(
            text=text,
            model=model,
        )
    async def embedding(
        self,
        text: str,
    ):

        return await self.llm.embedding(
            text,
        )
    async def health_check(self):

        return {
            "service": "ChatService",
            "healthy": True,
            "llm": True,
            "memory": True,
            "tools": True,
        }