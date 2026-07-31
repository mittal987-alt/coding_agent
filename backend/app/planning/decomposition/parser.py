# parser.py
from __future__ import annotations

import json
import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from .models import Goal
from .prompts import GOAL_PARSER_PROMPT

logger = logging.getLogger(__name__)


class GoalParser:
    """
    Converts natural language requests into structured Goal objects.
    """

    def __init__(
        self,
        llm: BaseChatModel,
    ) -> None:
        self.llm = llm

    async def parse(
        self,
        request: str,
    ) -> Goal:
        """
        Parse a user request.

        Example:
            "Build a FastAPI expense tracker with JWT authentication."
        """

        messages = [
            SystemMessage(content=GOAL_PARSER_PROMPT),
            HumanMessage(content=request),
        ]

        response = await self.llm.ainvoke(messages)

        try:

            data = json.loads(response.content)

            return Goal.model_validate(data)

        except Exception:

            logger.exception("Goal parsing failed.")

            return Goal(
                title=request,
                description=request,
                requirements=[],
                constraints=[],
            )