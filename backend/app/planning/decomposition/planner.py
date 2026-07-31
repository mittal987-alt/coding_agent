# planner.py
from __future__ import annotations

import json
import logging
from uuid import uuid4

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from .models import (
    Goal,
    TaskGraph,
    TaskNode,
)
from .prompts import TASK_PLANNER_PROMPT

logger = logging.getLogger(__name__)


class TaskPlanner:
    """
    Generates an executable task graph from a Goal.
    """

    def __init__(
        self,
        llm: BaseChatModel,
    ) -> None:
        self.llm = llm

    async def plan(
        self,
        goal: Goal,
    ) -> TaskGraph:
        """
        Generate a task graph.
        """

        messages = [

            SystemMessage(
                content=TASK_PLANNER_PROMPT,
            ),

            HumanMessage(
                content=goal.model_dump_json(
                    indent=2,
                ),
            ),
        ]

        response = await self.llm.ainvoke(
            messages,
        )

        try:

            raw_tasks = json.loads(
                response.content,
            )

            tasks = []

            for item in raw_tasks:

                tasks.append(

                    TaskNode(

                        id=item.get(
                            "id",
                            str(uuid4()),
                        ),

                        title=item["title"],

                        description=item[
                            "description"
                        ],

                        agent=item.get(
                            "agent",
                            "planner",
                        ),

                        priority=item.get(
                            "priority",
                            "medium",
                        ),

                        estimated_minutes=item.get(
                            "estimated_minutes",
                            10,
                        ),

                        dependencies=item.get(
                            "dependencies",
                            [],
                        ),

                        metadata=item.get(
                            "metadata",
                            {},
                        ),
                    )

                )

            return TaskGraph(

                goal=goal,

                tasks=tasks,

            )

        except Exception:

            logger.exception(
                "Planning failed."
            )

            raise