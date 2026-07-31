"""
Base Agent

All AI agents inherit from this class.

Responsibilities

- LLM access
- Prompt execution
- Logging
- Error handling
- Tool execution
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

from app.graph.state import AgentState


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        name: str,
    ):

        self.llm = llm
        self.name = name

    @abstractmethod
    async def run(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Execute the agent.
        """
        ...

    async def invoke_llm(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        messages = [

            SystemMessage(
                content=system_prompt
            ),

            HumanMessage(
                content=user_prompt
            ),
        ]

        response = await self.llm.ainvoke(
            messages
        )

        return response.content

    def log(
        self,
        message: str,
    ) -> None:

        logger.info(
            "[%s] %s",
            self.name,
            message,
        )

    def update_state(
        self,
        state: AgentState,
        **kwargs: Any,
    ) -> AgentState:

        for key, value in kwargs.items():

            setattr(
                state,
                key,
                value,
            )

        return state

    async def safe_run(
        self,
        state: AgentState,
    ) -> AgentState:

        try:

            self.log("Starting execution")

            result = await self.run(
                state
            )

            self.log("Execution completed")

            return result

        except Exception as exc:

            logger.exception(exc)

            state.response = str(exc)

            return state