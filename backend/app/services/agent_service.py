from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from app.config.settings import Settings
from app.services.base import BaseService
from app.core.exceptions import (
    AgentExecutionError,
    NotFoundError,
)
class AgentService(BaseService):
    """
    Main orchestrator for autonomous AI execution.
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

        self.running_tasks: dict[str, asyncio.Task] = {}
    @property
    def planner(self):
        return self.resolve("planner")


    @property
    def memory(self):
        return self.resolve("memory_manager")


    @property
    def tools(self):
        return self.resolve("tool_registry")


    @property
    def llm(self):
        return self.resolve("llm_manager")


    @property
    def workspace(self):
        return self.resolve("workspace_manager")


    @property
    def agent_manager(self):
        return self.resolve("agent_manager")
    async def run(
        self,
        *,
        goal: str,
        workspace: str,
        model: str | None = None,
        context: dict | None = None,
    ):

        task_id = str(uuid.uuid4())

        task = asyncio.create_task(

            self._execute(

                task_id=task_id,

                goal=goal,

                workspace=workspace,

                model=model,

                context=context or {},
            )
        )

        self.running_tasks[task_id] = task

        return {
            "task_id": task_id,
            "status": "queued",
        }
    async def _execute(
        self,
        *,
        task_id: str,
        goal: str,
        workspace: str,
        model: str | None,
        context: dict,
    ):

        try:

            plan = await self.planner.plan(

                goal=goal,

                workspace=workspace,
            )

            result = None

            for step in plan.steps:

                result = await self.agent_manager.execute(

                    step=step,

                    workspace=workspace,

                    model=model,

                    context=context,
                )

            await self.publish(

                "agent.completed",

                {
                    "task_id": task_id,
                },
            )

            return result

        except Exception as exc:

            raise AgentExecutionError(
                str(exc),
            ) from exc
    async def status(
        self,
        task_id: str,
    ):

        task = self.running_tasks.get(task_id)

        if task is None:
            raise NotFoundError(
                "Task not found."
            )

        if task.done():

            return {
                "status": "completed",
            }

        return {
            "status": "running",
        }
    async def result(
        self,
        task_id: str,
    ):

        task = self.running_tasks.get(task_id)

        if task is None:
            raise NotFoundError(
                "Task not found."
            )

        return await task
    async def cancel(
        self,
        task_id: str,
    ):

        task = self.running_tasks.get(task_id)

        if task is None:
            raise NotFoundError(
                "Task not found."
            )

        task.cancel()

        return True
    async def retry(
        self,
        *,
        goal: str,
        workspace: str,
        model: str | None = None,
    ):

        return await self.run(

            goal=goal,

            workspace=workspace,

            model=model,
        )
    async def running(self):

        return list(

            self.running_tasks.keys()
        )
    async def logs(
        self,
        task_id: str,
    ):

        return await self.memory.logs(
            task_id,
        )
    async def progress(
        self,
        task_id: str,
    ):

        return await self.memory.progress(
            task_id,
        )
    async def execute_parallel(
        self,
        agents: list,
    ):

        return await asyncio.gather(

            *agents,
        )
    async def plan(
        self,
        goal: str,
        workspace: str,
    ):

        return await self.planner.plan(

            goal=goal,

            workspace=workspace,
        )
    async def estimate_cost(
        self,
        goal: str,
        model: str,
    ):

        tokens = await self.llm.estimate_tokens(
            goal,
            model,
        )

        return await self.llm.estimate_cost(

            model=model,

            tokens=tokens,
        )
    async def health_check(self):

        return {

            "service": "AgentService",

            "healthy": True,

            "planner": True,

            "tools": True,

            "memory": True,
        }