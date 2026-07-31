
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import UTC, datetime

from .models import (
    Conversation,
    ConversationMessage,
    ConversationStatistics,
    ConversationSummary,
)


class BaseConversationStorage(ABC):
    """
    Abstract storage backend for conversation memory.
    """

    @abstractmethod
    async def create_conversation(
        self,
        conversation: Conversation,
    ) -> Conversation:
        ...

    @abstractmethod
    async def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        ...

    @abstractmethod
    async def update_conversation(
        self,
        conversation: Conversation,
    ) -> Conversation:
        ...

    @abstractmethod
    async def delete_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        ...

    @abstractmethod
    async def list_conversations(
        self,
        *,
        project_id: str | None = None,
        user_id: str | None = None,
    ) -> list[Conversation]:
        ...

    @abstractmethod
    async def add_message(
        self,
        conversation_id: str,
        message: ConversationMessage,
    ) -> None:
        ...

    @abstractmethod
    async def get_messages(
        self,
        conversation_id: str,
    ) -> list[ConversationMessage]:
        ...

    @abstractmethod
    async def add_summary(
        self,
        conversation_id: str,
        summary: ConversationSummary,
    ) -> None:
        ...

    @abstractmethod
    async def get_summaries(
        self,
        conversation_id: str,
    ) -> list[ConversationSummary]:
        ...

    @abstractmethod
    async def statistics(
        self,
        conversation_id: str,
    ) -> ConversationStatistics:
        ...


class InMemoryConversationStorage(BaseConversationStorage):
    """
    Reference in-memory implementation.
    """

    def __init__(self) -> None:

        self._conversations: dict[str, Conversation] = {}

        self._messages: defaultdict[
            str,
            list[ConversationMessage],
        ] = defaultdict(list)

        self._summaries: defaultdict[
            str,
            list[ConversationSummary],
        ] = defaultdict(list)

    async def create_conversation(
        self,
        conversation: Conversation,
    ) -> Conversation:

        self._conversations[conversation.id] = conversation

        return conversation

    async def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:

        return self._conversations.get(conversation_id)

    async def update_conversation(
        self,
        conversation: Conversation,
    ) -> Conversation:

        conversation.updated_at = datetime.now(UTC)

        self._conversations[conversation.id] = conversation

        return conversation

    async def delete_conversation(
        self,
        conversation_id: str,
    ) -> bool:

        existed = conversation_id in self._conversations

        self._conversations.pop(conversation_id, None)
        self._messages.pop(conversation_id, None)
        self._summaries.pop(conversation_id, None)

        return existed

    async def list_conversations(
        self,
        *,
        project_id: str | None = None,
        user_id: str | None = None,
    ) -> list[Conversation]:

        conversations = list(self._conversations.values())

        if project_id:

            conversations = [
                c
                for c in conversations
                if c.project_id == project_id
            ]

        if user_id:

            conversations = [
                c
                for c in conversations
                if c.user_id == user_id
            ]

        conversations.sort(
            key=lambda c: c.last_activity,
            reverse=True,
        )

        return conversations

    async def add_message(
        self,
        conversation_id: str,
        message: ConversationMessage,
    ) -> None:

        conversation = self._conversations[conversation_id]

        self._messages[conversation_id].append(message)

        conversation.messages.append(message)

        conversation.total_messages += 1

        conversation.total_tokens += message.token_count

        conversation.last_activity = datetime.now(UTC)

        conversation.updated_at = conversation.last_activity

    async def get_messages(
        self,
        conversation_id: str,
    ) -> list[ConversationMessage]:

        return list(self._messages.get(conversation_id, []))

    async def add_summary(
        self,
        conversation_id: str,
        summary: ConversationSummary,
    ) -> None:

        conversation = self._conversations[conversation_id]

        self._summaries[conversation_id].append(summary)

        conversation.summaries.append(summary)

    async def get_summaries(
        self,
        conversation_id: str,
    ) -> list[ConversationSummary]:

        return list(self._summaries.get(conversation_id, []))

    async def statistics(
        self,
        conversation_id: str,
    ) -> ConversationStatistics:

        conversation = self._conversations[conversation_id]

        messages = self._messages[conversation_id]

        user_messages = sum(
            1
            for m in messages
            if m.role.value == "user"
        )

        assistant_messages = sum(
            1
            for m in messages
            if m.role.value == "assistant"
        )

        tool_messages = sum(
            1
            for m in messages
            if m.role.value == "tool"
        )

        average = (
            conversation.total_tokens / conversation.total_messages
            if conversation.total_messages
            else 0.0
        )

        return ConversationStatistics(
            conversation_id=conversation.id,
            total_messages=conversation.total_messages,
            user_messages=user_messages,
            assistant_messages=assistant_messages,
            tool_messages=tool_messages,
            summaries=len(conversation.summaries),
            total_tokens=conversation.total_tokens,
            average_tokens_per_message=average,
            started_at=conversation.created_at,
            last_activity=conversation.last_activity,
        )