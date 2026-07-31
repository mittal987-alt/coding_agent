from __future__ import annotations

import json
import uuid
from datetime import datetime

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.memory.manager import MemoryManager
from app.memory.models import (
    MemoryEntry,
    MemoryType,
)

from app.prompts.memory import (
    MEMORY_SYSTEM_PROMPT,
)


class MemoryAgent(BaseAgent):

    def __init__(
        self,
        llm,
        manager: MemoryManager,
    ):

        super().__init__(
            llm,
            "Memory",
        )

        self.manager = manager

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        prompt = f"""
User Request

{state.user_request}

Plan

{state.plan}

Generated Code

{state.generated_code}

Review

{state.review}

Tests

{state.test_output}
"""

        response = await self.invoke_llm(

            MEMORY_SYSTEM_PROMPT,

            prompt,

        )

        data = json.loads(response)

        for item in data["memories"]:

            memory = MemoryEntry(

                id=str(uuid.uuid4()),

                memory_type=MemoryType(
                    item["type"]
                ),

                content=item["content"],

                created_at=datetime.utcnow(),

            )

            self.manager.add(memory)

        state.memory_count = len(
            self.manager.entries
        )

        return state