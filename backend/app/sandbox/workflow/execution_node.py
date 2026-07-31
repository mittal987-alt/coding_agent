from __future__ import annotations

import logging
from typing import Any

from app.agents.terminal_agent import TerminalAgent
from app.core.event_bus import Event, EventBus
from app.sandbox.exceptions.base import SandboxException
from langgraph.graph import StateGraph
logger = logging.getLogger(__name__)


class ExecutionNode:
    """
    LangGraph execution node.

    Responsible for:

    - Publishing execution events
    - Calling TerminalAgent
    - Handling sandbox failures
    - Updating workflow state
    """

    def __init__(
        self,
        terminal_agent: TerminalAgent,
        event_bus: EventBus,
    ) -> None:

        self.terminal_agent = terminal_agent
        self.event_bus = event_bus

    async def run(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:

        execution_id = state.get("execution_id")

        await self.event_bus.publish(
            Event(
                name="execution_started",
                execution_id=execution_id,
                payload={
                    "workspace": state["workspace"],
                    "command": state["command"],
                },
            )
        )

        try:

            result = await self.terminal_agent.run(state)

            state["execution_result"] = result["execution_result"]

            await self.event_bus.publish(
                Event(
                    name="execution_completed",
                    execution_id=execution_id,
                    payload={
                        "success": result["execution_result"]["success"],
                        "exit_code": result["execution_result"]["exit_code"],
                    },
                )
            )

            return state

        except SandboxException as exc:

            logger.exception("Sandbox execution failed")

            state["execution_error"] = {
                "code": exc.code,
                "message": str(exc),
                "retryable": exc.retryable,
                "severity": exc.severity.value,
            }

            await self.event_bus.publish(
                Event(
                    name="execution_failed",
                    execution_id=execution_id,
                    payload=state["execution_error"],
                )
            )

            raise

        except Exception as exc:

            logger.exception("Unexpected execution failure")

            state["execution_error"] = {
                "code": "UNKNOWN_ERROR",
                "message": str(exc),
                "retryable": False,
                "severity": "critical",
            }

            await self.event_bus.publish(
                Event(
                    name="execution_failed",
                    execution_id=execution_id,
                    payload=state["execution_error"],
                )
            )

            raise


    

workflow = StateGraph(dict)

workflow.add_node(
    "execute",
    execution_node.run,
)

workflow.set_entry_point("execute")