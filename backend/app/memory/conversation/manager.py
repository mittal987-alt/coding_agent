# conversation/manager.py
from __future__ import annotations

import logging
from datetime import UTC, datetime

from .models import (
    ContextWindow,
    Conversation,
    ConversationMessage,
    ConversationRole,
    ConversationStatistics,
    ConversationSummary,
)
from .storage import BaseConversationStorage

logger = logging.getLogger(__name__)


class ConversationMemoryManager:
    """
    High-level conversation memory manager.

    Responsibilities:
    - Conversation lifecycle
    - Message management
    - Context window generation
    - Automatic summarization
    - Token budgeting
    """

    def __init__(
        self,
        storage: BaseConversationStorage,
        *,
        max_context_tokens: int = 16000,
        summary_trigger_messages: int = 40,
    ) -> None:

        self.storage = storage

        self.max_context_tokens = max_context_tokens

        self.summary_trigger_messages = summary_trigger_messages

    # ------------------------------------------------------------------
    # Conversation Lifecycle
    # ------------------------------------------------------------------

    async def create_conversation(
        self,
        *,
        title: str = "Untitled Conversation",
        user_id: str | None = None,
        project_id: str | None = None,
        agent_id: str | None = None,
    ) -> Conversation:

        conversation = Conversation(
            title=title,
            user_id=user_id,
            project_id=project_id,
            agent_id=agent_id,
        )

        return await self.storage.create_conversation(
            conversation
        )

    async def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:

        return await self.storage.get_conversation(
            conversation_id
        )

    async def list_conversations(
        self,
        *,
        project_id: str | None = None,
        user_id: str | None = None,
    ) -> list[Conversation]:

        return await self.storage.list_conversations(
            project_id=project_id,
            user_id=user_id,
        )

    async def delete_conversation(
        self,
        conversation_id: str,
    ) -> bool:

        return await self.storage.delete_conversation(
            conversation_id
        )

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    async def add_message(
        self,
        *,
        conversation_id: str,
        role: ConversationRole,
        content: str,
        token_count: int = 0,
        metadata: dict | None = None,
    ) -> ConversationMessage:

        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            metadata=metadata or {},
        )

        await self.storage.add_message(
            conversation_id,
            message,
        )

        await self._auto_summarize(
            conversation_id
        )

        return message

    async def history(
        self,
        conversation_id: str,
    ) -> list[ConversationMessage]:

        return await self.storage.get_messages(
            conversation_id
        )

    # ------------------------------------------------------------------
    # Context Window
    # ------------------------------------------------------------------

    async def build_context(
        self,
        conversation_id: str,
    ) -> ContextWindow:

        messages = await self.storage.get_messages(
            conversation_id
        )

        summaries = await self.storage.get_summaries(
            conversation_id
        )

        total = 0

        selected: list[ConversationMessage] = []

        for message in reversed(messages):

            if (
                total + message.token_count
                > self.max_context_tokens
            ):
                break

            total += message.token_count

            selected.insert(
                0,
                message,
            )

        return ContextWindow(
            messages=selected,
            summaries=summaries,
            total_tokens=total,
            max_tokens=self.max_context_tokens,
            truncated=len(selected) != len(messages),
        )

    # ------------------------------------------------------------------
    # Summarization
    # ------------------------------------------------------------------

    async def _auto_summarize(
        self,
        conversation_id: str,
    ) -> None:

        messages = await self.storage.get_messages(
            conversation_id
        )

        if len(messages) < self.summary_trigger_messages:
            return

        summaries = await self.storage.get_summaries(
            conversation_id
        )

        already = sum(
            s.message_count
            for s in summaries
        )

        remaining = messages[already:]

        if len(remaining) < self.summary_trigger_messages:
            return

        batch = remaining[
            : self.summary_trigger_messages
        ]

        text = "\n".join(
            m.content
            for m in batch
        )

        summary = ConversationSummary(
            conversation_id=conversation_id,
            summary=text[:2000],
            message_count=len(batch),
            start_message_id=batch[0].id,
            end_message_id=batch[-1].id,
            token_count=sum(
                m.token_count
                for m in batch
            ),
        )

        await self.storage.add_summary(
            conversation_id,
            summary,
        )

    # ------------------------------------------------------------------
    # Prompt Building
    # ------------------------------------------------------------------

    async def prompt_messages(
        self,
        conversation_id: str,
    ) -> list[dict]:

        context = await self.build_context(
            conversation_id
        )

        prompt = []

        for summary in context.summaries:

            prompt.append(
                {
                    "role": "system",
                    "content": (
                        "Conversation Summary:\n"
                        + summary.summary
                    ),
                }
            )

        for message in context.messages:

            prompt.append(
                {
                    "role": message.role.value,
                    "content": message.content,
                }
            )

        return prompt

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    async def statistics(
        self,
        conversation_id: str,
    ) -> ConversationStatistics:

        return await self.storage.statistics(
            conversation_id
        )

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    async def archive_idle(
        self,
        *,
        days: int = 30,
    ) -> int:
        """
        Placeholder for future archival policy.
        """

        logger.info(
            "Archive conversations idle for %d days",
            days,
        )

        return 0