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

from langchain_core.language_models.chat_models import BaseChatModel

from app.graph.state import AgentState
from app.core.observability import traced_llm_call

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
        """
        Invoke the LLM with system + user messages.

        Automatically traces to LangSmith when LANGCHAIN_TRACING_V2=true
        and LANGCHAIN_API_KEY is set. Falls back to direct invocation
        with zero overhead when tracing is disabled.
        """
        return await traced_llm_call(
            agent_name=self.name,
            llm=self.llm,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

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